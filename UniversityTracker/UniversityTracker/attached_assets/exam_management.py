from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QDialog, QFormLayout, QLineEdit, QDateEdit, QSpinBox,
                             QTextEdit, QMessageBox, QGroupBox, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor


class ExamDialog(QDialog):
    """Dialog for adding or editing an exam record."""
    
    def __init__(self, parent=None, exam=None, max_grade=30, pass_threshold=18):
        super(ExamDialog, self).__init__(parent)
        self.exam = exam  # None for new exam, existing exam dict for editing
        self.max_grade = max_grade
        self.pass_threshold = pass_threshold
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        if self.exam:
            self.setWindowTitle("Modifica Esame")
        else:
            self.setWindowTitle("Aggiungi Nuovo Esame")
            
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Exam name
        self.name_input = QLineEdit()
        if self.exam:
            self.name_input.setText(self.exam['name'])
        layout.addRow("Nome Esame:", self.name_input)
        
        # Credits
        self.credits_input = QSpinBox()
        self.credits_input.setMinimum(1)
        self.credits_input.setMaximum(30)  # Reasonable max for university courses
        if self.exam:
            self.credits_input.setValue(self.exam['credits'])
        else:
            self.credits_input.setValue(6)  # Default common value
        layout.addRow("CFU:", self.credits_input)
        
        # Status group
        status_group = QGroupBox("Stato")
        status_layout = QVBoxLayout()
        
        self.status_passed = QRadioButton("Superato")
        self.status_failed = QRadioButton("Non Superato")
        self.status_planned = QRadioButton("Pianificato")
        
        status_layout.addWidget(self.status_passed)
        status_layout.addWidget(self.status_failed)
        status_layout.addWidget(self.status_planned)
        
        status_group.setLayout(status_layout)
        layout.addRow(status_group)
        
        # Set default status
        if self.exam:
            if self.exam['status'] == 'passed':
                self.status_passed.setChecked(True)
            elif self.exam['status'] == 'failed':
                self.status_failed.setChecked(True)
            else:
                self.status_planned.setChecked(True)
        else:
            self.status_planned.setChecked(True)
        
        # Grade (only enabled for passed exams)
        self.grade_input = QSpinBox()
        self.grade_input.setMinimum(self.pass_threshold)
        self.grade_input.setMaximum(self.max_grade)
        if self.exam and self.exam['grade'] is not None:
            self.grade_input.setValue(self.exam['grade'])
        else:
            self.grade_input.setValue(self.pass_threshold)
        
        # Make sure grade is only enabled if status is 'passed'
        self.grade_input.setEnabled(self.status_passed.isChecked())
        layout.addRow("Voto:", self.grade_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        if self.exam and self.exam['date']:
            try:
                date = QDate.fromString(self.exam['date'], "yyyy-MM-dd")
                self.date_input.setDate(date)
            except:
                pass
        layout.addRow("Data:", self.date_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        if self.exam and self.exam['notes']:
            self.notes_input.setText(self.exam['notes'])
        layout.addRow("Note:", self.notes_input)
        
        # Connect signals
        self.status_passed.toggled.connect(self.update_grade_enabled)
        self.status_failed.toggled.connect(self.update_grade_enabled)
        self.status_planned.toggled.connect(self.update_grade_enabled)
        
        # Initial state
        self.update_grade_enabled()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salva")
        self.cancel_button = QPushButton("Annulla")
        
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
        
    def update_grade_enabled(self):
        """Enable or disable grade input based on selected status."""
        self.grade_input.setEnabled(self.status_passed.isChecked())
        
    def get_exam_data(self):
        """Get exam data from form inputs."""
        status = ''
        if self.status_passed.isChecked():
            status = 'passed'  # Manteniamo i valori inglesi nel database
        elif self.status_failed.isChecked():
            status = 'failed'  # Manteniamo i valori inglesi nel database
        else:
            status = 'planned'  # Manteniamo i valori inglesi nel database
            
        grade = None
        if status == 'passed':
            grade = self.grade_input.value()
            
        return {
            'name': self.name_input.text(),
            'credits': self.credits_input.value(),
            'status': status,
            'grade': grade,
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'notes': self.notes_input.toPlainText()
        }


class ExamManagementWidget(QWidget):
    """Widget for managing exams (add, edit, delete)."""
    
    # Signal emitted when exams are updated
    exams_updated = pyqtSignal()
    
    def __init__(self, db_manager):
        super(ExamManagementWidget, self).__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_exams()
        
    def init_ui(self):
        """Initialize the exam management UI."""
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Gestione Esami")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Filters and controls
        controls_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tutti gli Esami", None)
        self.filter_combo.addItem("Superati", "passed")
        self.filter_combo.addItem("Non Superati", "failed")
        self.filter_combo.addItem("Pianificati", "planned")
        self.filter_combo.currentIndexChanged.connect(self.filter_exams)
        
        self.add_button = QPushButton("Aggiungi Esame")
        self.add_button.clicked.connect(self.add_exam)
        
        controls_layout.addWidget(QLabel("Filtro:"))
        controls_layout.addWidget(self.filter_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.add_button)
        
        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        main_layout.addWidget(controls_widget)
        
        # Exams table
        self.exams_table = QTableWidget()
        self.exams_table.setColumnCount(7)
        self.exams_table.setHorizontalHeaderLabels(
            ["ID", "Nome Esame", "CFU", "Voto", "Stato", "Data", "Azioni"])
        
        # Configure table properties
        self.exams_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch name column
        self.exams_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions column
        self.exams_table.verticalHeader().setVisible(False)
        self.exams_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.exams_table.setSelectionMode(QTableWidget.SingleSelection)
        self.exams_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        main_layout.addWidget(self.exams_table)
        
        self.setLayout(main_layout)
        
    def load_exams(self, status=None):
        """Load exams from database into the table."""
        # Get settings
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        
        # Clear table
        self.exams_table.setRowCount(0)
        
        # Get exams
        exams = self.db_manager.get_all_exams(status)
        
        # Populate table
        for row, exam in enumerate(exams):
            self.exams_table.insertRow(row)
            
            # ID (hidden)
            id_item = QTableWidgetItem(str(exam['id']))
            id_item.setData(Qt.UserRole, exam['id'])
            self.exams_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(exam['name'])
            self.exams_table.setItem(row, 1, name_item)
            
            # Credits
            credits_item = QTableWidgetItem(str(exam['credits']))
            credits_item.setTextAlignment(Qt.AlignCenter)
            self.exams_table.setItem(row, 2, credits_item)
            
            # Grade
            grade_text = str(exam['grade']) if exam['grade'] is not None else "-"
            grade_item = QTableWidgetItem(grade_text)
            grade_item.setTextAlignment(Qt.AlignCenter)
            self.exams_table.setItem(row, 3, grade_item)
            
            # Status with color
            status_text = "Superato" if exam['status'] == 'passed' else "Non Superato" if exam['status'] == 'failed' else "Pianificato"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            if exam['status'] == 'passed':
                status_item.setBackground(QColor(200, 255, 200))  # Light green
            elif exam['status'] == 'failed':
                status_item.setBackground(QColor(255, 200, 200))  # Light red
            else:  # planned
                status_item.setBackground(QColor(200, 200, 255))  # Light blue
                
            self.exams_table.setItem(row, 4, status_item)
            
            # Date
            date_text = exam['date'] if exam['date'] else "-"
            date_item = QTableWidgetItem(date_text)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.exams_table.setItem(row, 5, date_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_button = QPushButton("Modifica")
            edit_button.setProperty("exam_id", exam['id'])
            edit_button.clicked.connect(self.edit_exam)
            
            # Calendar button for planned exams
            if exam['status'] == 'planned':
                calendar_button = QPushButton("Pianifica")
                calendar_button.setProperty("exam_id", exam['id'])
                calendar_button.clicked.connect(self.schedule_exam)
                actions_layout.addWidget(calendar_button)
            
            delete_button = QPushButton("Elimina")
            delete_button.setProperty("exam_id", exam['id'])
            delete_button.clicked.connect(self.delete_exam)
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            actions_widget.setLayout(actions_layout)
            self.exams_table.setCellWidget(row, 6, actions_widget)
            
        # Hide ID column
        self.exams_table.hideColumn(0)
        
        # Resize columns to contents
        self.exams_table.resizeColumnsToContents()
        
    def filter_exams(self):
        """Filter exams based on selected status."""
        status = self.filter_combo.currentData()
        self.load_exams(status)
        
    def refresh_data(self):
        """Reload exams from database with current filter."""
        status = self.filter_combo.currentData()
        self.load_exams(status)
        
    def add_exam(self):
        """Open dialog to add a new exam."""
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        pass_threshold = int(self.db_manager.get_setting('pass_threshold', 18))
        
        dialog = ExamDialog(self, max_grade=max_grade, pass_threshold=pass_threshold)
        if dialog.exec_() == QDialog.Accepted:
            exam_data = dialog.get_exam_data()
            
            # Add to database
            exam_id = self.db_manager.add_exam(
                name=exam_data['name'],
                credits=exam_data['credits'],
                grade=exam_data['grade'],
                status=exam_data['status'],
                date=exam_data['date'],
                notes=exam_data['notes']
            )
            
            if exam_id:
                # Refresh table
                self.load_exams(self.filter_combo.currentData())
                # Emit signal to update other views
                self.exams_updated.emit()
                QMessageBox.information(self, "Operazione Completata", "Esame aggiunto con successo.")
            else:
                QMessageBox.warning(self, "Errore", "Impossibile aggiungere l'esame.")
                
    def edit_exam(self):
        """Edit selected exam."""
        try:
            button = self.sender()
            if button:
                exam_id = button.property("exam_id")
                
                # Get exam data
                exam = self.db_manager.get_exam(exam_id)
                if not exam:
                    QMessageBox.warning(self, "Errore", "Esame non trovato.")
                    return
                    
                max_grade = int(self.db_manager.get_setting('max_grade', 30))
                pass_threshold = int(self.db_manager.get_setting('pass_threshold', 18))
                
                dialog = ExamDialog(self, exam=exam, max_grade=max_grade, pass_threshold=pass_threshold)
                if dialog.exec_() == QDialog.Accepted:
                    exam_data = dialog.get_exam_data()
                    
                    # Ensure grade is None if status is not 'passed'
                    if exam_data['status'] != 'passed':
                        exam_data['grade'] = None
                    
                    # Update in database
                    success = self.db_manager.update_exam(
                        exam_id=exam_id,
                        name=exam_data['name'],
                        credits=exam_data['credits'],
                        grade=exam_data['grade'],
                        status=exam_data['status'],
                        date=exam_data['date'],
                        notes=exam_data['notes']
                    )
                    
                    if success:
                        # Refresh table
                        self.load_exams(self.filter_combo.currentData())
                        # Emit signal to update other views
                        self.exams_updated.emit()
                        QMessageBox.information(self, "Operazione Completata", "Esame aggiornato con successo.")
                    else:
                        QMessageBox.warning(self, "Errore", "Impossibile aggiornare l'esame.")
        except Exception as e:
            QMessageBox.critical(self, "Errore Critico", f"Si è verificato un errore durante la modifica dell'esame: {str(e)}")
                    
    def delete_exam(self):
        """Delete selected exam."""
        button = self.sender()
        if button:
            exam_id = button.property("exam_id")
            
            # Confirm deletion
            reply = QMessageBox.question(
                self, 'Conferma Eliminazione',
                "Sei sicuro di voler eliminare questo esame?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Delete from database
                success = self.db_manager.delete_exam(exam_id)
                
                if success:
                    # Refresh table
                    self.load_exams(self.filter_combo.currentData())
                    # Emit signal to update other views
                    self.exams_updated.emit()
                    QMessageBox.information(self, "Operazione Completata", "Esame eliminato con successo.")
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile eliminare l'esame.")
                    
    def schedule_exam(self):
        """Schedule an exam on the calendar."""
        button = self.sender()
        if button:
            exam_id = button.property("exam_id")
            
            # Get exam data
            exam = self.db_manager.get_exam(exam_id)
            if not exam:
                QMessageBox.warning(self, "Errore", "Esame non trovato.")
                return
                
            # Check if there are existing calendar events for this exam
            events = self.db_manager.get_calendar_events(exam_id=exam_id)
            
            if events:
                # Confirm overwrite
                reply = QMessageBox.question(
                    self, 'Pianificazione Esame',
                    "Questo esame è già pianificato nel calendario. Vuoi modificare l'evento esistente?",
                    QMessageBox.Yes | QMessageBox.No, 
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Open calendar tab and edit the event
                    self.parent().tab_widget.setCurrentIndex(3)  # Switch to calendar tab
                    self.parent().calendar.edit_event(events[0])
            else:
                # Create new event for this exam
                
                # Determine a default date if not set
                exam_date = None
                if exam['date']:
                    exam_date = QDate.fromString(exam['date'], "yyyy-MM-dd")
                else:
                    exam_date = QDate.currentDate().addDays(30)  # Default to 30 days from now
                
                # Create event
                start_date = exam_date.toString("yyyy-MM-dd") + "T09:00:00"
                end_date = exam_date.toString("yyyy-MM-dd") + "T11:00:00"
                
                event_id = self.db_manager.add_calendar_event(
                    title=f"Esame: {exam['name']}",
                    event_type="exam",
                    start_date=start_date,
                    end_date=end_date,
                    exam_id=exam_id,
                    all_day=False,
                    description=f"Esame di {exam['name']} - {exam['credits']} CFU"
                )
                
                if event_id:
                    # Update exam date
                    self.db_manager.update_exam(
                        exam_id=exam_id,
                        date=exam_date.toString("yyyy-MM-dd")
                    )
                    
                    QMessageBox.information(
                        self, 
                        "Esame Pianificato", 
                        f"L'esame '{exam['name']}' è stato pianificato per il {exam_date.toString('dd/MM/yyyy')}.\n\n"
                        f"Vai alla scheda Calendario per visualizzare e modificare i dettagli."
                    )
                    
                    # Refresh data
                    self.load_exams(self.filter_combo.currentData())
                    self.exams_updated.emit()
                else:
                    QMessageBox.warning(self, "Errore", "Impossibile pianificare l'esame.")
