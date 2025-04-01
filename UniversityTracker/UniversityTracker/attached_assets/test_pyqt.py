"""
Script semplice per testare l'installazione di PyQt5.
Esegui questo script per verificare che PyQt5 sia installato correttamente.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Test PyQt5')
        self.setGeometry(300, 300, 300, 200)
        
        layout = QVBoxLayout()
        
        label = QLabel('PyQt5 è installato correttamente!')
        layout.addWidget(label)
        
        button = QPushButton('Chiudi')
        button.clicked.connect(self.close)
        layout.addWidget(button)
        
        test_button = QPushButton('Test Messagebox')
        test_button.clicked.connect(self.show_message)
        layout.addWidget(test_button)
        
        self.setLayout(layout)
        
    def show_message(self):
        QMessageBox.information(self, 'Test', 'Tutto funziona correttamente!')


if __name__ == '__main__':
    print("Avvio del test di PyQt5...")
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    print("Finestra di prova aperta. Se la vedi, PyQt5 è installato correttamente.")
    sys.exit(app.exec_())