import csv
import os
import pymysql
import pandas as pd
from datetime import datetime
import hashlib
import time

def generate_eas_alert(row, folder_name):
    # Liste des messages d'erreur
    alert_messages = {
        "CONNECT_FAILURE": "Échec de connexion. Cause possible: Problème réseau ou serveur non accessible.",
        "TLS_HANDSHAKE_FAILURE": "Échec de la négociation TLS. Cause possible: Certificat invalide ou problème de compatibilité TLS.",
        "CERTIFICATE_EXPIRED": "Certificat expiré. Cause possible: Certificat non renouvelé.",
        "CERTIFICATE_INVALID": "Certificat invalide. Cause possible: Erreur de configuration ou certificat compromis.",
        "DNS_FAILURE": "Échec de la résolution DNS. Cause possible: Domaine introuvable ou problème réseau.",
        "TIMEOUT": "Délai d'attente dépassé. Cause possible: Serveur lent ou problème de connexion.",
        "HTTP_403": "Accès refusé. Cause possible: Droits insuffisants.",
        "HTTP_404": "Ressource non trouvée. Cause possible: URL incorrecte.",
        "HTTP_500": "Erreur interne du serveur. Cause possible: Problème côté serveur cible.",
        "HTTP_502": "Mauvaise passerelle. Cause possible: Serveur intermédiaire non fonctionnel.",
        "HTTP_503": "Service indisponible. Cause possible: Maintenance ou surcharge du serveur.",
        "HTTP_504": "Délai d'attente de la passerelle dépassé. Cause possible: Serveur cible lent.",
        "PROXY_AUTH_FAILURE": "Échec d'authentification au proxy. Cause possible: Identifiants incorrects.",
        "SERVICE_UNAVAILABLE": "Service indisponible. Cause possible: Maintenance ou surcharge.",
    }
    
    # Récupérer les champs pertinents
    status = row.get("status", "")
    event_id = row.get("event-id", "")
    tls_status = row.get("tls-status", "")
    http_status = row.get("http-status", "")
    error_code = row.get("error-code", "")
    
    # Vérifier les erreurs et générer une alerte si nécessaire
    if event_id in alert_messages:
        return f"ALERTE: {alert_messages[event_id]} Dossier: {folder_name}."
    elif tls_status in ["TLS_HANDSHAKE_FAILURE", "CERTIFICATE_EXPIRED", "CERTIFICATE_INVALID"]:
        return f"ALERTE: {alert_messages[tls_status]} Dossier: {folder_name}."
    elif http_status in ["403", "404", "500", "502", "503", "504"]:
        return f"ALERTE: Erreur HTTP {http_status} dans le dossier {folder_name}. Cause probable: {alert_messages.get(f'HTTP_{http_status}', 'Erreur inconnue')}."
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
    Génère un hash unique pour chaque ligne de log 
    pour éviter les doublons
    """
    # Sélectionnez les champs les plus significatifs pour créer un hash unique
    hash_fields = [
        row.get('date-time', ''),  # Timestamp
        row.get('client-ip', ''),  # Adresse IP du client
        row.get('destination-ip', ''),  # Adresse IP de destination
        row.get('request-method', ''),  # Méthode HTTP (GET, POST, etc.)
        row.get('request-url', ''),  # URL de la requête
        row.get('user-agent', ''),  # User-Agent
        row.get('status-code', '')
    ]
    hash_string = '|'.join(hash_fields)
    return hashlib.md5(hash_string.encode()).hexdigest()

def is_log_line_processed(cursor, log_hash):
    """
    Vérifie si une ligne de log a déjà été traitée
    """
    cursor.execute("SELECT COUNT(*) FROM rpchttp_logs WHERE log_hash = %s", (log_hash,))
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
            alert = generate_eas_alert(row, folder_name)
            if alert:
                row["ID"] = len(logs_with_errors) + 1
                row["explication"] = alert
                logs_with_errors.append(row)

            # Préparer les données pour l'insertion
            data = tuple(
                row.get(column, None) if pd.notna(row.get(column)) and row.get(column) != '' else None
                for column in [
                    "DateTime", "RequestId", "MajorVersion", "MinorVersion", "BuildVersion", "RevisionVersion",
                    "ClientRequestId", "Protocol", "UrlHost", "UrlStem", "ProtocolAction", "AuthenticationType",
                    "IsAuthenticated", "AuthenticatedUser", "Organization", "AnchorMailbox", "UserAgent",
                    "ClientIpAddress", "ServerHostName", "HttpStatus", "BackEndStatus", "ErrorCode", "Method",
                    "ProxyAction", "TargetServer", "TargetServerVersion", "RoutingType", "RoutingHint",
                    "BackEndCookie", "ServerLocatorHost", "ServerLocatorLatency", "RequestBytes", "ResponseBytes",
                    "TargetOutstandingRequests", "AuthModulePerfContext", "HttpPipelineLatency",
                    "CalculateTargetBackEndLatency", "GlsLatencyBreakup", "TotalGlsLatency",
                    "AccountForestLatencyBreakup", "TotalAccountForestLatency", "ResourceForestLatencyBreakup",
                    "TotalResourceForestLatency", "ADLatency", "SharedCacheLatencyBreakup",
                    "TotalSharedCacheLatency", "ActivityContextLifeTime", "ModuleToHandlerSwitchingLatency",
                    "ClientReqStreamLatency", "BackendReqInitLatency", "BackendReqStreamLatency",
                    "BackendProcessingLatency", "BackendRespInitLatency", "BackendRespStreamLatency",
                    "ClientRespStreamLatency", "KerberosAuthHeaderLatency", "HandlerCompletionLatency",
                    "RequestHandlerLatency", "HandlerToModuleSwitchingLatency", "ProxyTime", "CoreLatency",
                    "RoutingLatency", "HttpProxyOverhead", "TotalRequestTime", "RouteRefresherLatency",
                    "UrlQuery", "BackEndGenericInfo", "GenericInfo", "GenericErrors", "EdgeTraceId", "DatabaseGuid",
                    "UserADObjectGuid", "PartitionEndpointLookupLatency", "RoutingStatus", "explication"
                ]
            )

            # Convertir les dates
            data = list(data)
            
            data[0] = convert_date_format(data[0])  # Date-time est en première position

            # Ajouter le hash à la liste des données
            data.append(log_hash)

            insert_sql = """
                INSERT INTO rpchttp_logs (
                    DateTime, RequestId, MajorVersion, MinorVersion, BuildVersion, RevisionVersion,
                    ClientRequestId, Protocol, UrlHost, UrlStem, ProtocolAction, AuthenticationType,
                    IsAuthenticated, AuthenticatedUser, Organization, AnchorMailbox, UserAgent,
                    ClientIpAddress, ServerHostName, HttpStatus, BackEndStatus, ErrorCode, Method,
                    ProxyAction, TargetServer, TargetServerVersion, RoutingType, RoutingHint,
                    BackEndCookie, ServerLocatorHost, ServerLocatorLatency, RequestBytes, ResponseBytes,
                    TargetOutstandingRequests, AuthModulePerfContext, HttpPipelineLatency,
                    CalculateTargetBackEndLatency, GlsLatencyBreakup, TotalGlsLatency,
                    AccountForestLatencyBreakup, TotalAccountForestLatency, ResourceForestLatencyBreakup,
                    TotalResourceForestLatency, ADLatency, SharedCacheLatencyBreakup,
                    TotalSharedCacheLatency, ActivityContextLifeTime, ModuleToHandlerSwitchingLatency,
                    ClientReqStreamLatency, BackendReqInitLatency, BackendReqStreamLatency,
                    BackendProcessingLatency, BackendRespInitLatency, BackendRespStreamLatency,
                    ClientRespStreamLatency, KerberosAuthHeaderLatency, HandlerCompletionLatency,
                    RequestHandlerLatency, HandlerToModuleSwitchingLatency, ProxyTime, CoreLatency,
                    RoutingLatency, HttpProxyOverhead, TotalRequestTime, RouteRefresherLatency,
                    UrlQuery, BackEndGenericInfo, GenericInfo, GenericErrors, EdgeTraceId, DatabaseGuid,
                    UserADObjectGuid, PartitionEndpointLookupLatency, RoutingStatus, explication, log_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s , %s
                        )
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
                directory_path = "C:/Users/Admin/Desktop/Projet Info/logs/httpsproxy/RpcHttp"
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