from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFormLayout, QLineEdit, QSpinBox, QGroupBox, QMessageBox,
                             QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SettingsWidget(QWidget):
    """Widget for application settings."""
    
    def __init__(self, db_manager):
        super(SettingsWidget, self).__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the settings UI."""
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Degree settings group
        degree_group = QGroupBox("Degree Settings")
        degree_layout = QFormLayout()
        
        self.degree_name_input = QLineEdit()
        degree_layout.addRow("Degree Name:", self.degree_name_input)
        
        self.total_credits_input = QSpinBox()
        self.total_credits_input.setMinimum(1)
        self.total_credits_input.setMaximum(500)  # High max for flexibility
        degree_layout.addRow("Total Credits Required:", self.total_credits_input)
        
        degree_group.setLayout(degree_layout)
        main_layout.addWidget(degree_group)
        
        # Grading system group
        grading_group = QGroupBox("Grading System")
        grading_layout = QFormLayout()
        
        self.max_grade_input = QSpinBox()
        self.max_grade_input.setMinimum(1)
        self.max_grade_input.setMaximum(100)
        grading_layout.addRow("Maximum Grade:", self.max_grade_input)
        
        self.pass_threshold_input = QSpinBox()
        self.pass_threshold_input.setMinimum(1)
        self.pass_threshold_input.setMaximum(100)
        grading_layout.addRow("Passing Threshold:", self.pass_threshold_input)
        
        grading_group.setLayout(grading_layout)
        main_layout.addWidget(grading_group)
        
        # Target settings group
        target_group = QGroupBox("Target Settings")
        target_layout = QFormLayout()
        
        self.target_average_input = QSpinBox()
        self.target_average_input.setMinimum(18)
        self.target_average_input.setMaximum(110)
        target_layout.addRow("Target Average (110 scale):", self.target_average_input)
        
        target_group.setLayout(target_layout)
        main_layout.addWidget(target_group)
        
        # Data management group
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout()
        
        export_import_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        
        self.import_button = QPushButton("Import Data")
        self.import_button.clicked.connect(self.import_data)
        
        export_import_layout.addWidget(self.export_button)
        export_import_layout.addWidget(self.import_button)
        
        data_layout.addLayout(export_import_layout)
        
        # Add reset button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        
        self.reset_button = QPushButton("Reset All Data")
        self.reset_button.setStyleSheet("background-color: #f44336; color: white;")
        self.reset_button.clicked.connect(self.reset_data)
        
        reset_layout.addWidget(self.reset_button)
        reset_layout.addStretch()
        
        data_layout.addLayout(reset_layout)
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)
        
        # Save button
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
    def load_settings(self):
        """Load settings from database into UI elements."""
        # Degree settings
        degree_name = self.db_manager.get_setting('degree_name', 'Computer Science')
        total_credits = int(self.db_manager.get_setting('total_credits', 180))
        
        # Grading system
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        pass_threshold = int(self.db_manager.get_setting('pass_threshold', 18))
        
        # Target settings
        target_average = int(self.db_manager.get_setting('target_average', 100))
        
        # Set values in UI
        self.degree_name_input.setText(degree_name)
        self.total_credits_input.setValue(total_credits)
        self.max_grade_input.setValue(max_grade)
        self.pass_threshold_input.setValue(pass_threshold)
        self.target_average_input.setValue(target_average)
        
    def save_settings(self):
        """Save settings from UI to database."""
        # Validate inputs
        if self.pass_threshold_input.value() > self.max_grade_input.value():
            QMessageBox.warning(self, "Invalid Settings", 
                              "Pass threshold cannot be greater than maximum grade.")
            return
            
        # Get values from UI
        degree_name = self.degree_name_input.text()
        total_credits = self.total_credits_input.value()
        max_grade = self.max_grade_input.value()
        pass_threshold = self.pass_threshold_input.value()
        target_average = self.target_average_input.value()
        
        # Save to database
        self.db_manager.update_setting('degree_name', degree_name)
        self.db_manager.update_setting('total_credits', str(total_credits))
        self.db_manager.update_setting('max_grade', str(max_grade))
        self.db_manager.update_setting('pass_threshold', str(pass_threshold))
        self.db_manager.update_setting('target_average', str(target_average))
        
        QMessageBox.information(self, "Settings Saved", 
                              "Your settings have been saved successfully.")
        
    def export_data(self):
        """Export database to a file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Data", "", "SQLite Database (*.db);;All Files (*)")
                
            if file_path:
                import sqlite3
                import shutil
                
                # Get current database path
                dbconn = self.db_manager.conn
                src_path = dbconn.execute("PRAGMA database_list").fetchone()[2]
                
                # Copy database file
                shutil.copy2(src_path, file_path)
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Data exported successfully to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                               f"Failed to export data: {str(e)}")
        
    def import_data(self):
        """Import database from a file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Data", "", "SQLite Database (*.db);;All Files (*)")
                
            if file_path:
                reply = QMessageBox.question(
                    self, 'Confirm Import',
                    "Importing data will replace your current data. Continue?",
                    QMessageBox.Yes | QMessageBox.No, 
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    import sqlite3
                    import shutil
                    
                    # Close current connection
                    self.db_manager.close()
                    
                    # Get current database path
                    import os
                    documents_folder = os.path.join(os.path.expanduser("~"), "Documents")
                    app_folder = os.path.join(documents_folder, "UniversityCareerManager")
                    db_path = os.path.join(app_folder, "university_career.db")
                    
                    # Copy imported database file
                    shutil.copy2(file_path, db_path)
                    
                    # Reopen connection
                    self.db_manager.conn = sqlite3.connect(db_path)
                    self.db_manager.conn.row_factory = sqlite3.Row
                    self.db_manager.cursor = self.db_manager.conn.cursor()
                    
                    # Refresh UI
                    self.load_settings()
                    
                    QMessageBox.information(self, "Import Successful", 
                                         "Data imported successfully. Please restart the application.")
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", 
                              f"Failed to import data: {str(e)}")
        
    def reset_data(self):
        """Reset all data in the database."""
        reply = QMessageBox.question(
            self, 'Confirm Reset',
            "This will delete ALL your data including exams and settings. "
            "This action cannot be undone. Are you sure?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Double check
            confirm = QMessageBox.question(
                self, 'Final Confirmation',
                "ALL DATA WILL BE PERMANENTLY DELETED. Proceed?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                try:
                    # Delete all exams
                    self.db_manager.cursor.execute("DELETE FROM exams")
                    
                    # Reset settings to default
                    self.db_manager.cursor.execute("DELETE FROM settings")
                    
                    # Insert default settings
                    default_settings = [
                        ('degree_name', 'Computer Science'),
                        ('total_credits', '180'),
                        ('target_average', '100'),
                        ('max_grade', '30'),
                        ('pass_threshold', '18')
                    ]
                    
                    for key, value in default_settings:
                        self.db_manager.cursor.execute('''
                        INSERT INTO settings (key, value)
                        VALUES (?, ?)
                        ''', (key, value))
                        
                    self.db_manager.conn.commit()
                    
                    # Reload settings
                    self.load_settings()
                    
                    QMessageBox.information(self, "Reset Complete", 
                                         "All data has been reset to default.")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Reset Failed", 
                                     f"Failed to reset data: {str(e)}")
