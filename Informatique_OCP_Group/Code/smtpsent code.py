import csv
import os
import pymysql
import pandas as pd
from datetime import datetime
import hashlib
import time


def generate_smtpsent_alert(row, folder_name):
    # Liste des messages d'erreur spécifiques à SMTP Sent
    alert_messages = {
        "CONNECT_FAILURE": "Échec de connexion au serveur SMTP. Cause possible: Problème réseau ou serveur non accessible.",
        "TLS_HANDSHAKE_FAILURE": "Échec de la négociation TLS. Cause possible: Certificat invalide ou problème de compatibilité TLS.",
        "DNS_FAILURE": "Échec de la résolution DNS. Cause possible: Domaine introuvable ou problème réseau.",
        "TIMEOUT": "Délai d'attente dépassé. Cause possible: Serveur lent ou problème de connexion.",
        "HTTP_403": "Accès refusé au serveur SMTP. Cause possible: Droits insuffisants.",
        "HTTP_404": "Ressource SMTP non trouvée. Cause possible: URL incorrecte.",
        "HTTP_500": "Erreur interne du serveur SMTP. Cause possible: Problème côté serveur de destination.",
        "AUTH_FAILURE": "Échec d'authentification SMTP. Cause possible: Identifiants incorrects ou configuration erronée.",
        "QUOTA_EXCEEDED": "Quota de messagerie dépassé. Cause possible: Limite d'envoi atteinte.",
        "MAILBOX_FULL": "Boîte aux lettres du destinataire pleine. Cause possible: Le destinataire ne peut pas recevoir de messages.",
        "SEND_FAILED": "Échec de l'envoi du message. Cause possible: Problème avec le serveur SMTP de destination.",
        "ADDRESS_REJECTED": "Adresse rejetée. Cause possible: Adresse invalide ou problème avec les règles du serveur.",
        "MAILBOX_DISABLED": "Boîte aux lettres du destinataire désactivée. Cause possible: Compte suspendu ou supprimé.",
        "BAD_SMTP_SERVER_RESPONSE": "Réponse incorrecte du serveur SMTP. Cause possible: Problème temporaire avec le serveur.",
        "SMTP_SERVER_BUSY": "Serveur SMTP trop occupé. Cause possible: Surcharge du serveur ou trop de requêtes simultanées.",
        "SPF_FAIL": "Échec de la vérification SPF. Cause possible: L'adresse de l'expéditeur n'est pas autorisée.",
        "DKIM_FAIL": "Échec de la vérification DKIM. Cause possible: Signature d'email non valide.",
        "DMARC_FAIL": "Échec de la politique DMARC. Cause possible: Le message a échoué à la vérification DMARC.",
        "RELAYS_DENIED": "Relais refusé par le serveur SMTP. Cause possible: Le serveur n'accepte pas de relayer le message.",
        "BLACKLISTED": "Serveur SMTP sur liste noire. Cause possible: L'adresse IP a été signalée.",
        "SMTP_TIMEOUT": "Délai d'attente SMTP dépassé. Cause possible: Le serveur a mis trop de temps à répondre.",
        "INVALID_RECIPIENT": "Destinataire invalide. Cause possible: Adresse e-mail incorrecte ou serveur non acceptant ce domaine.",
        "ERROR_SENDING_MESSAGE": "Erreur générale lors de l'envoi du message. Cause possible: Problème temporaire ou défaillance serveur.",
    }

    # Récupérer les champs pertinents
    status = row.get("status", "")
    event_id = row.get("event-id", "")
    error_code = row.get("error-code", "")
    
    # Vérifier les erreurs et générer une alerte si nécessaire
    if event_id in alert_messages:
        return f"ALERTE: {alert_messages[event_id]} Dossier: {folder_name}."
    elif status != "SUCCESS":
        return f"ALERTE: Statut inattendu '{status}' détecté dans le dossier {folder_name}."
    elif error_code:
        return f"ALERTE: Erreur détectée avec le code '{error_code}' dans le dossier {folder_name}."
    
    return None


    
    
    
def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Erreur de conversion de la date : {e}, date reçue : {date_str}")
        return None



def generate_hash_for_log_line(row):
    """
    Génère un hash unique pour chaque ligne de log SMTP
    pour éviter les doublons
    """
    # Sélectionnez les champs les plus significatifs pour créer un hash unique
    hash_fields = [
        row.get('date-time', ''),     # Timestamp
        row.get('connector-id', ''),  # Identifiant du connecteur
        row.get('session-id', ''),    # Identifiant de session
        row.get('sequence-number', ''),  # Numéro de séquence
        row.get('local-endpoint', ''),   # Point de terminaison local
        row.get('remote-endpoint', ''),  # Point de terminaison distant
        row.get('event', ''),         # Type d'événement
        row.get('context', '')        # Contexte de l'événement
    ]
    hash_string = '|'.join(hash_fields)
    return hashlib.md5(hash_string.encode()).hexdigest()

def is_log_line_processed(cursor, log_hash):
    """
    Vérifie si une ligne de log a déjà été traitée
    """
    cursor.execute("SELECT COUNT(*) FROM smtpsent_logs WHERE log_hash = %s", (log_hash,))
    return cursor.fetchone()[0] > 0

def process_log_file(input_file_path, folder_name, cursor, connection):
    try:
        with open(input_file_path, 'r') as file:
            headers, data_lines = None, []
            for line in file:
                if line.startswith("#Fields:"):
                    headers = line.strip("#Fields:").strip().split(",")
                elif headers:
                    data_lines.append(line.strip())

        if not headers:
            print(f"Aucun en-tête trouvé dans le fichier {input_file_path}.")
            return

        csv_reader = csv.DictReader(data_lines, fieldnames=headers)
        logs_with_errors = []
        processed_lines = 0
        skipped_lines = 0

        for row in csv_reader:
            # Générer un hash unique pour la ligne
            log_hash = generate_hash_for_log_line(row)

            # Vérifier si la ligne a déjà été traitée
            if is_log_line_processed(cursor, log_hash):
                skipped_lines += 1
                continue

            # Vérifier les erreurs et générer une alerte si nécessaire
            alert = generate_smtpsent_alert(row, folder_name)
            if alert:
                row["ID"] = len(logs_with_errors) + 1
                row["explication"] = alert
                logs_with_errors.append(row)

            # Préparer les données pour l'insertion
            # Récupérer les champs et gérer les valeurs manquantes
            data = tuple(
                row.get(column, None) if pd.notna(row.get(column)) and row.get(column) != '' else None
                for column in [
                    "date-time", "connector-id", "session-id", "sequence-number", "local-endpoint", "remote-endpoint",
                    "event", "data", "context", "explication"
                ]
            )
            
            # Convertir la date (si nécessaire)
            data = list(data)
            data[0] = convert_date_format(data[0])  # La date-time est en première position

            # Ajouter le hash à la liste des données
            data.append(log_hash)
            
            # Préparer l'instruction SQL pour l'insertion
            insert_sql = """
                INSERT INTO smtpsent_logs (
                    date_time, connector_id, session_id, sequence_number, local_endpoint, remote_endpoint, event, data, context, explication, log_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(insert_sql, data)
            connection.commit()
            processed_lines += 1

        print(f"{len(logs_with_errors)} erreurs détectées dans {input_file_path}.")
        print(f"Lignes traitées: {processed_lines}, Lignes ignorées : {skipped_lines}")

    except Exception as e:
        print(f"Erreur lors du traitement du fichier {input_file_path}: {e}")
        
        
def process_all_logs_in_directory(directory_path, cursor, connection):
    for filename in os.listdir(directory_path):
        if filename.endswith(".LOG"):
            input_file_path = os.path.join(directory_path, filename)
            folder_name = os.path.basename(directory_path)
            print(f"Traitement du fichier: {filename}")
            process_log_file(input_file_path, folder_name, cursor, connection)


    
    
def main():
    while True:
        try:
            # Connexion à la base de données MySQL
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='root',
                database='projetinfo'
            )
            
            with connection.cursor() as cursor:
                directory_path = "C:/Users/Admin/Desktop/Projet Info/logs/SmtpReceive"
                process_all_logs_in_directory(directory_path, cursor, connection)
            
            connection.close()
            print("Traitement terminé. Prochaine exécution dans 10 secondes...")
            
            # Attendre 10 secondes avant la prochaine itération
            time.sleep(10)

        except Exception as e:
            print(f"Une erreur est survenue : {e}")
            print("Réessai dans 10 secondes...")
            time.sleep(10)

if __name__ == "__main__":
    main()