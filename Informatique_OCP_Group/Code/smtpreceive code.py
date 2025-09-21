import csv
import os
import pymysql
import pandas as pd
from datetime import datetime
import hashlib
import time


def generate_smtpreceive_alert(row, folder_name):
    # Liste des messages d'erreur SMTP
    alert_messages = {
        "RecvAuthFailed": "Échec de l'authentification. Cause possible: Identifiants incorrects ou configuration manquante.",
        "Disconnect": "Déconnexion inattendue. Cause possible: Perte de connexion ou déconnexion côté client.",
        "BlockedConnection": "Connexion rejetée. Cause possible: Liste noire ou règle de filtrage anti-spam.",
        "DnsFailure": "Échec de la résolution DNS. Cause possible: Domaine introuvable ou problème réseau.",
        "QuotaExceeded": "Quota dépassé. Cause possible: Limites d'utilisation du serveur atteintes.",
        "CommandUnrecognized": "Commande SMTP non reconnue. Cause possible: Erreur dans la syntaxe ou commande non supportée.",
        "InvalidSenderAddress": "Adresse de l'expéditeur non valide. Cause possible: Syntaxe incorrecte ou domaine inexistant.",
        "InvalidRecipientAddress": "Adresse du destinataire non valide. Cause possible: Syntaxe incorrecte ou domaine inexistant.",
        "DeliveryFailure": "Échec de la livraison. Cause possible: Problème de configuration ou de routage.",
        "TlsNegotiationFailed": "Échec de la négociation TLS. Cause possible: Problème de certificat ou de configuration TLS.",
        "ContentFilterFailed": "Filtrage du contenu échoué. Cause possible: Message jugé comme spam ou malveillant.",
        "TooManyConnections": "Trop de connexions. Cause possible: Limite de connexions simultanées atteinte.",
        "ReceiveTimeout": "Délai d'attente de réception dépassé. Cause possible: Serveur distant lent ou problème de connexion.",
        "SendTimeout": "Délai d'attente d'envoi dépassé. Cause possible: Serveur distant lent ou problème de connexion.",
        "CommandSyntaxError": "Erreur de syntaxe dans la commande. Cause possible: Commande SMTP incorrecte.",
        "SpamDetected": "Spam détecté. Cause possible: Le message a été jugé comme spam par le serveur.",
        "BlacklistedSender": "Expéditeur en liste noire. Cause possible: Le domaine ou l'IP de l'expéditeur est sur une liste noire.",
    }
    
    # Récupérer les champs pertinents
    event = row.get("event", "")
    data = row.get("data", "")
    context = row.get("context", "")
    status = row.get("status", "")
    error_code = row.get("error-code", "")
    
    # Vérifier les erreurs et générer une alerte si nécessaire
    if event in alert_messages:
        return f"ALERTE: {alert_messages[event]} Dossier: {folder_name}."
    elif status != "SUCCESS":
        return f"ALERTE: Statut inattendu '{status}' détecté dans le dossier {folder_name}.",
    elif error_code:
        return f"ALERTE: Erreur détectée avec le code '{error_code}' dans le dossier {folder_name}."
    elif "spam" in data.lower():
        return f"ALERTE: Message détecté comme spam dans le dossier {folder_name}.",
    elif "blacklist" in context.lower():
        return f"ALERTE: Expéditeur sur liste noire dans le dossier {folder_name}.",
    
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
    cursor.execute("SELECT COUNT(*) FROM smtpreceive_logs WHERE log_hash = %s", (log_hash,))
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
            alert = generate_smtpreceive_alert(row, folder_name)
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
                INSERT INTO smtpreceive_logs (
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