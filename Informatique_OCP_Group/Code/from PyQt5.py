from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application PyQt")

        # Layout et widgets
        layout = QVBoxLayout()
        button = QPushButton("Cliquez ici")
        layout.addWidget(button)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

# Application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
