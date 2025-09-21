import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

def run_powershell_command(command):
    try:
        process = subprocess.Popen(
            ["powershell.exe", "-Command", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return stdout.strip(), stderr.strip()
    except Exception as e:
        return None, str(e)

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Storage Exchange (Temps Réel)")
        self.setGeometry(100, 100, 1000, 700)

        # Mise en page principale
        layout = QVBoxLayout()

        # Étiquette d'état
        self.status_label = QLabel("Dernière mise à jour : Jamais")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 12px;
                margin: 5px;
            }
        """)
        layout.addWidget(self.status_label)

        # Figure avec esthétique améliorée
        plt.style.use('ggplot')
        self.figure = Figure(figsize=(10, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Conteneur principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer pour mise à jour périodique
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute_storage_command)
        self.timer.start(10000)  # 10000 ms = 10 secondes

        # Exécution initiale
        self.execute_storage_command()

    def execute_storage_command(self):
        from datetime import datetime
        
        command = (
            "Add-PSSnapin Microsoft.Exchange.Management.PowerShell.SnapIn; "
            "Get-MailboxDatabase -Status | Select-Object Name, DatabaseSize, AvailableNewMailboxSpace"
        )
        output, error = run_powershell_command(command)

        # Mise à jour de l'étiquette de statut
        current_time = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"Dernière mise à jour : {current_time}")

        if error:
            self.plot_error_state(error)
        elif output:
            self.parse_and_plot(output)
        else:
            self.plot_error_state("Aucune donnée récupérée")

    def plot_error_state(self, error_message):
        # Effacer la figure précédente
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Afficher un message d'erreur
        ax.text(0.5, 0.5, f"Erreur:\n{error_message}", 
                horizontalalignment='center', 
                verticalalignment='center', 
                color='red', 
                fontsize=12)
        
        ax.set_title('Erreur de Récupération', color='red')
        ax.axis('off')
        
        self.canvas.draw()

    def parse_and_plot(self, output):
        lines = output.splitlines()

        for line in lines:
            if "Mailbox Database 0430573603" in line:
                try:
                    parts = line.split()

                    database_size = float(parts[3].replace("MB", "").replace(",", "").strip())
                    available_space = float(parts[7].replace("MB", "").replace(",", "").strip())

                    used_space = database_size - available_space
                    total_space = database_size

                    free_space_percentage = (available_space / total_space) * 100

                    # Effacer la figure précédente
                    self.figure.clear()
                    
                    # Créer un sous-graphique
                    ax = self.figure.add_subplot(111)

                    # Palette de couleurs
                    used_color = '#e74c3c' if free_space_percentage < 10 else '#3498db'

                    # Graphique à secteurs pour l'utilisation de l'espace
                    sizes = [used_space, available_space]
                    labels = ['Espace Utilisé', 'Espace Disponible']
                    colors = [used_color, '#34495e']

                    wedges, texts, autotexts = ax.pie(
                        sizes, 
                        labels=labels, 
                        colors=colors, 
                        autopct='%1.1f%%', 
                        startangle=90, 
                        wedgeprops=dict(edgecolor='white', linewidth=1),
                        textprops={'fontsize': 10, 'color': 'white', 'weight': 'bold'}
                    )

                    # Titre personnalisé
                    ax.set_title('Stockage Base de Données Exchange', 
                                 fontsize=16, 
                                 fontweight='bold', 
                                 color='#2c3e50',
                                 pad=20)

                    # Annotation avec les détails
                    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
                    info_text = (
                        f"Espace Total: {total_space:.2f} MB\n"
                        f"Espace Utilisé: {used_space:.2f} MB\n"
                        f"Espace Disponible: {available_space:.2f} MB"
                    )
                    ax.text(1.05, 0.5, info_text, transform=ax.transAxes, fontsize=10,
                            verticalalignment='center', bbox=props)

                    # Améliorer l'esthétique de la figure
                    self.figure.tight_layout()
                    self.canvas.draw()
                    return

                except (ValueError, IndexError) as e:
                    self.plot_error_state(f"Erreur de traitement : {str(e)}")
                    return

        self.plot_error_state("Aucune donnée valide pour le graphique")

# Lancement de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())
