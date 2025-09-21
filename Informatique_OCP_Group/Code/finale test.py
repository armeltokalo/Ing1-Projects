import csv
import os
import pymysql
import pandas as pd
from datetime import datetime
import hashlib

def generate_message_tracking_alert(row, folder_name):
    # Liste des événements problématiques et leurs messages
    alert_messages = {
        "BADRECIPIENT": "Problème de destinataire. Cause possible: Destinataire invalide ou inconnu.",
        "DELIVERYFAILURE": "Échec de la livraison. Cause possible: Problème de serveur ou de réseau.",
        "INVALIDRECIPIENT": "Destinataire invalide. Cause possible: Adresse incorrecte.",
        "REJECTED": "Message rejeté. Cause possible: Problème de serveur de destination.",
        "HAREDIRECTFAIL": "Échec de redirection. Cause possible: Serveur de redirection introuvable.",
        "ROUTEFAIL": "Échec du routage. Cause possible: Problème de configuration du serveur.",
        "AUTHFAIL": "Échec de l'authentification. Cause possible: Identifiants incorrects.",
        "SERVERERROR": "Erreur interne du serveur. Cause possible: Surcharge serveur.",
        "SERVICEUNAVAILABLE": "Service de messagerie indisponible. Cause possible: Maintenance ou panne.",
        "TIMEOUT": "Délai d'attente dépassé. Cause possible: Problème de connexion ou de serveur.",
        "TEMPFAIL": "Échec temporaire. Cause possible: Problème temporaire du serveur.",
        "BOUNCE": "Message en échec de remise. Cause possible: Boîte pleine ou destinataire non trouvé.",
    }
    
    recipient_status = row.get("recipient-status", "")
    event_id = row.get("event-id", "")
    
    # Générer une alerte si nécessaire
    if recipient_status != "250 2.1.5 Recipient OK" or None:
        return f"ALERTE: Problème de livraison pour le destinataire {row['recipient-address']} dans le dossier {folder_name}. Statut du destinataire: {recipient_status}."
    elif event_id in alert_messages:
        return f"ALERTE: {alert_messages[event_id]} Dossier: {folder_name}."
    
    
    
def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Erreur de conversion de la date : {e}, date reçue : {date_str}")
        return None



def generate_hash_for_log_line(row):
    """
    Génère un hash unique pour chaque ligne de log 
    pour éviter les doublons
    """
    # Sélectionnez les champs les plus significatifs pour créer un hash unique
    hash_fields = [
        row.get('date-time', ''), 
        row.get('recipient-address', ''), 
        row.get('event-id', ''), 
        row.get('internal-message-id', '')
    ]
    hash_string = '|'.join(hash_fields)
    return hashlib.md5(hash_string.encode()).hexdigest()

def is_log_line_processed(cursor, log_hash):
    """
    Vérifie si une ligne de log a déjà été traitée
    """
    cursor.execute("SELECT COUNT(*) FROM message_tracking_logs WHERE log_hash = %s", (log_hash,))
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
            alert = generate_message_tracking_alert(row, folder_name)
            if alert:
                row["ID"] = len(logs_with_errors) + 1
                row["explication"] = alert
                logs_with_errors.append(row)

            # Préparer les données pour l'insertion
            data = tuple(
                row.get(column, None) if pd.notna(row.get(column)) and row.get(column) != '' else None
                for column in [
                    "date-time", "client-ip", "client-hostname", "server-ip", "server-hostname", 
                    "source-context", "connector-id", "source", "event-id", "internal-message-id", 
                    "message-id", "network-message-id", "recipient-address", "recipient-status", 
                    "total-bytes", "recipient-count", "related-recipient-address", "reference", 
                    "message-subject", "sender-address", "return-path", "message-info", 
                    "directionality", "tenant-id", "original-client-ip", "original-server-ip", 
                    "custom-data", "transport-traffic-type", "log-id", "schema-version", "explication"
                ]
            )

            # Convertir les dates
            data = list(data)
            data[0] = convert_date_format(data[0])  # Date-time est en première position

            # Ajouter le hash à la liste des données
            data.append(log_hash)

            insert_sql = """
                INSERT INTO message_tracking_logs (
                    date_time, client_ip, client_hostname, server_ip, server_hostname, 
                    source_context, connector_id, source, event_id, internal_message_id, 
                    message_id, network_message_id, recipient_address, recipient_status, 
                    total_bytes, recipient_count, related_recipient_address, reference, 
                    message_subject, sender_address, return_path, message_info, 
                    directionality, tenant_id, original_client_ip, original_server_ip, 
                    custom_data, transport_traffic_type, log_id, schema_version, explication,
                    log_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, data)
            connection.commit()
            processed_lines += 1

        print(f"{len(logs_with_errors)} erreurs détectées dans {input_file_path}.")
        print(f"Lignes traitées et inserées: {processed_lines}, Lignes ignorées (déjà traitées et inserées) : {skipped_lines}")

    except Exception as e:
        print(f"Erreur lors du traitement du fichier {input_file_path}: {e}")
        
        
def process_all_logs_in_directory(directory_path, cursor, connection):
    for filename in os.listdir(directory_path):
        if filename.endswith(".LOG"):
            input_file_path = os.path.join(directory_path, filename)
            folder_name = os.path.basename(directory_path)
            print(f"Traitement du fichier: {filename}")
            process_log_file(input_file_path, folder_name, cursor, connection)

# Connexion à la base de données MySQL
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='projetinfo'
    )
    with connection.cursor() as cursor:
        directory_path = "C:/Users/Admin/Desktop/Projet Info/logs/MessageTracking"
        process_all_logs_in_directory(directory_path, cursor, connection)
finally:
    connection.close()
    print("Connexion à la base de données fermée.")