import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import signal

from database import DatabaseManager
# Import directly from files in the root directory instead of from views package
from dashboard import DashboardWidget
from exam_management import ExamManagementWidget
from analytics import AnalyticsWidget
from settings import SettingsWidget
from calendar_view import AcademicCalendarWidget

class UniversityCareerManager(QMainWindow):
    """Main application window for University Career Manager."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Setup UI
        self.setWindowTitle("Gestione Carriera Universitaria")
        self.setGeometry(100, 100, 1000, 700)
        # Use a generated icon instead as it might not find the original asset
        self.setWindowIcon(QIcon("generated-icon.png"))
        
        # Load stylesheet
        self.load_stylesheet()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create widgets for each tab
        self.dashboard = DashboardWidget(self.db_manager)
        self.exam_management = ExamManagementWidget(self.db_manager)
        self.analytics = AnalyticsWidget(self.db_manager)
        self.calendar = AcademicCalendarWidget(self.db_manager)
        self.settings = SettingsWidget(self.db_manager)
        
        # Add tabs to widget
        self.tab_widget.addTab(self.dashboard, "Panoramica")
        self.tab_widget.addTab(self.exam_management, "Gestione Esami")
        self.tab_widget.addTab(self.analytics, "Analisi")
        self.tab_widget.addTab(self.calendar, "Calendario")
        self.tab_widget.addTab(self.settings, "Impostazioni")
        
        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        
        # Set up central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Connect signals
        self.setup_signals()
        
    def load_stylesheet(self):
        """Load application style from QSS file."""
        try:
            # Updated to look for style.qss directly in the current directory
            style_file = os.path.join(os.path.dirname(__file__), "style.qss")
            with open(style_file, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
    
    def setup_signals(self):
        """Connect signals between different parts of the application."""
        # When exams are updated, refresh all tabs
        self.exam_management.exams_updated.connect(self.dashboard.refresh_data)
        self.exam_management.exams_updated.connect(self.analytics.refresh_data)
        self.exam_management.exams_updated.connect(self.calendar.refresh_calendar)
        
        # When calendar events are updated, refresh related tabs
        self.calendar.examUpdated.connect(self.exam_management.refresh_data)
        self.calendar.examUpdated.connect(self.dashboard.refresh_data)
        self.calendar.examUpdated.connect(self.analytics.refresh_data)
    
    def closeEvent(self, event):
        """Handle application close event."""
        reply = QMessageBox.question(
            self, 'Conferma Uscita',
            "Sei sicuro di voler uscire?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Close database connection
            self.db_manager.close()
            event.accept()
        else:
            event.ignore()


def main():
    """Entry point for the application."""
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Use VNC mode for Replit environment
    os.environ["QT_QPA_PLATFORM"] = "vnc"
    print("Starting in VNC mode...")
    
    print("Avvio di Gestione Carriera Universitaria...")
    
    app = QApplication(sys.argv)
    window = UniversityCareerManager()
    window.show()
    
    # Print a message when ready
    print("Application loaded successfully!")
    print("Note: This is running in a headless environment on Replit.")
    print("The PyQt interface isn't visible, but the application is running.")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()