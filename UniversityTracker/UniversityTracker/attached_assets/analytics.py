from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QFormLayout, QLineEdit, QSpinBox, QGroupBox, QScrollArea,
                             QFrame, QGridLayout, QSizePolicy, QDialog, QDialogButtonBox,
                             QDoubleSpinBox, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from calculations import AcademicCalculator

class LineChartWidget(FigureCanvas):
    """Widget for displaying trend charts."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(LineChartWidget, self).__init__(self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def update_chart(self, exams, title, y_label):
        """Update the line chart with new data."""
        self.axes.clear()
        
        # Sort exams by date
        sorted_exams = sorted([e for e in exams if e['date'] and e['status'] == 'passed'], 
                             key=lambda x: x['date'])
        
        if not sorted_exams:
            self.axes.text(0.5, 0.5, "No data to display", 
                          horizontalalignment='center', verticalalignment='center')
            self.draw()
            return
            
        dates = [e['date'] for e in sorted_exams]
        grades = [e['grade'] for e in sorted_exams]
        
        # Calculate cumulative average at each point
        cum_grades = []
        for i in range(len(grades)):
            cum_grades.append(sum(grades[:i+1]) / (i+1))
        
        # Plot grades and cumulative average
        self.axes.plot(range(len(dates)), grades, 'o-', label='Grades')
        self.axes.plot(range(len(dates)), cum_grades, 'r--', label='Cumulative Average')
        
        # Add labels and title
        self.axes.set_xlabel('Exams (chronological)')
        self.axes.set_ylabel(y_label)
        self.axes.set_title(title)
        
        # Set x-ticks
        if len(dates) > 10:
            # Only show some of the dates if there are too many
            step = len(dates) // 10 + 1
            self.axes.set_xticks(range(0, len(dates), step))
            self.axes.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45)
        else:
            self.axes.set_xticks(range(len(dates)))
            self.axes.set_xticklabels(dates, rotation=45)
        
        self.axes.legend()
        self.fig.tight_layout()
        self.draw()


class GradeEditDialog(QDialog):
    """Dialog for manually setting a target grade for an exam."""
    
    def __init__(self, parent=None, exam_name="", current_grade=0, max_grade=30):
        super(GradeEditDialog, self).__init__(parent)
        self.setWindowTitle("Imposta Voto Target")
        self.exam_name = exam_name
        self.max_grade = max_grade
        self.init_ui(current_grade)
        
    def init_ui(self, current_grade):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()
        
        # Information label
        info_label = QLabel(
            f"Stai impostando manualmente il voto target per l'esame '{self.exam_name}'.\n" +
            "Gli altri voti verranno ricalcolati automaticamente per mantenere la media obiettivo.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Form layout for grade input
        form_layout = QFormLayout()
        
        # Grade spinner
        self.grade_spinner = QDoubleSpinBox()
        self.grade_spinner.setMinimum(18)  # Minimum passing grade
        self.grade_spinner.setMaximum(self.max_grade)
        self.grade_spinner.setDecimals(1)
        self.grade_spinner.setSingleStep(0.5)
        self.grade_spinner.setValue(current_grade)
        form_layout.addRow("Voto Target:", self.grade_spinner)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Reset button to remove manual setting
        reset_button = QPushButton("Ripristina Calcolo Automatico")
        reset_button.clicked.connect(self.reset_value)
        layout.addWidget(reset_button)
        
        self.setLayout(layout)
        
    def reset_value(self):
        """Mark this grade to be reset to automatic calculation."""
        self.grade_spinner.setValue(-1)  # Use -1 as a special value to indicate reset
        self.accept()
        
    def get_grade(self):
        """Get the selected grade value."""
        return self.grade_spinner.value()


class CustomGradeSpinBox(QDoubleSpinBox):
    """Custom SpinBox for grade editing with signals for immediate updates."""
    
    # Signal emitted when the value changes
    valueModified = pyqtSignal(int, float)  # exam_id, new_grade
    
    def __init__(self, exam_id, parent=None):
        super(CustomGradeSpinBox, self).__init__(parent)
        self.exam_id = exam_id
        self.valueChanged.connect(self.on_value_changed)
        
    def on_value_changed(self, value):
        """Emit the valueModified signal with the exam_id and new value."""
        self.valueModified.emit(self.exam_id, value)


class TargetCalculationWidget(QWidget):
    """Widget for calculating target grades needed to reach desired average."""
    
    def __init__(self, db_manager, calculator):
        super(TargetCalculationWidget, self).__init__()
        self.db_manager = db_manager
        self.calculator = calculator
        self.required_grades = {}  # Store the current required grades
        self.custom_grades = {}    # Store custom grades for manual mode
        self.mode = "auto"         # Default mode: "auto" or "manual"
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI for target calculation."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Calcolo Voti Target")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form group
        form_group = QGroupBox("Parametri Obiettivo")
        form_layout = QFormLayout()
        
        # Target average input
        self.target_avg_input = QSpinBox()
        self.target_avg_input.setMinimum(18)
        self.target_avg_input.setMaximum(110)
        
        # Get current target from settings
        target_avg = int(self.db_manager.get_setting('target_average', 100))
        self.target_avg_input.setValue(target_avg)
        
        form_layout.addRow("Media Obiettivo (scala 110):", self.target_avg_input)
        
        # Calculate button
        self.calc_button = QPushButton("Calcola")
        self.calc_button.clicked.connect(self.calculate_targets)
        form_layout.addRow(self.calc_button)
        
        # Reset all fixed grades button
        self.reset_button = QPushButton("Ripristina Tutti i Voti Automatici")
        self.reset_button.clicked.connect(self.reset_all_fixed_grades)
        self.reset_button.setEnabled(False)  # Initially disabled
        form_layout.addRow(self.reset_button)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        self.auto_mode_radio = QRadioButton("Modalità Automatica")
        self.auto_mode_radio.setChecked(True)
        self.auto_mode_radio.toggled.connect(self.toggle_mode)
        
        self.manual_mode_radio = QRadioButton("Modalità Libera")
        self.manual_mode_radio.toggled.connect(self.toggle_mode)
        
        mode_layout.addWidget(self.auto_mode_radio)
        mode_layout.addWidget(self.manual_mode_radio)
        form_layout.addRow("Modalità:", mode_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Results table
        results_label = QLabel("Voti Necessari per l'Obiettivo (clicca su un voto per modificarlo manualmente)")
        results_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Esame", "CFU", "Voto Necessario"])
        
        # Configure table properties
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.cellDoubleClicked.connect(self.handle_grade_cell_click)
        
        layout.addWidget(self.results_table)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.summary_label)
        
        # Instructions label for Auto mode
        self.auto_instructions = QLabel("Doppio click su un voto nella tabella per modificarlo manualmente. " +
                                      "Gli altri voti verranno ricalcolati automaticamente.")
        self.auto_instructions.setWordWrap(True)
        self.auto_instructions.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.auto_instructions)
        
        # Instructions label for Manual mode
        self.manual_instructions = QLabel("Modifica liberamente i voti per vedere come cambia la media finale. " +
                                        "Ogni modifica aggiorna immediatamente la media prevista.")
        self.manual_instructions.setWordWrap(True)
        self.manual_instructions.setStyleSheet("color: gray; font-style: italic;")
        self.manual_instructions.setVisible(False)  # Initially hidden
        layout.addWidget(self.manual_instructions)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.calculate_targets()
        
    def handle_grade_cell_click(self, row, column):
        """Handle click on a grade cell to edit the target grade."""
        # Only allow editing the grade column
        if column != 2 or row >= len(self.exam_rows_map):
            return
            
        # Get exam information
        exam_id, exam = self.exam_rows_map[row]
        
        # Get current grade
        current_grade_value = self.required_grades.get(exam_id, 0)
        if isinstance(current_grade_value, tuple):
            current_grade_value = current_grade_value[0]  # Extract grade from tuple
            
        # Show edit dialog
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        dialog = GradeEditDialog(self, exam['name'], current_grade_value, max_grade)
        
        if dialog.exec_() == QDialog.Accepted:
            new_grade = dialog.get_grade()
            
            if new_grade < 0:
                # User wants to reset this fixed grade
                self.reset_fixed_grade(exam_id)
            else:
                # User set a specific grade
                self.update_with_fixed_grade(exam_id, new_grade)
    
    def reset_fixed_grade(self, exam_id):
        """Reset a fixed grade back to automatic calculation."""
        # Filter out this grade from fixed grades
        fixed_grades = {id: grade[0] for id, grade in self.required_grades.items() 
                       if isinstance(grade, tuple) and id != exam_id}
        
        # Recalculate grades with updated fixed grades
        target_avg = self.target_avg_input.value()
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        target_avg_scaled = (target_avg / 110) * max_grade
        
        all_exams = self.db_manager.get_all_exams()
        planned_exams = self.db_manager.get_planned_exams()
        
        self.required_grades = self.calculator.calculate_required_grades(
            all_exams, planned_exams, target_avg_scaled, max_grade, fixed_grades)
            
        # Mark remaining fixed grades
        for id, grade in fixed_grades.items():
            self.required_grades[id] = (grade, True)
            
        self.update_results_table()
            
    def reset_all_fixed_grades(self):
        """Reset all fixed grades and recalculate targets."""
        self.required_grades = {}  # Clear all fixed grades
        self.calculate_targets()  # Recalculate with no fixed grades
        
    def update_with_fixed_grade(self, exam_id, fixed_grade):
        """Update calculation with a manually fixed grade."""
        target_avg = self.target_avg_input.value()
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        target_avg_scaled = (target_avg / 110) * max_grade
        
        all_exams = self.db_manager.get_all_exams()
        planned_exams = self.db_manager.get_planned_exams()
        
        # Calculate new required grades with the fixed grade
        self.required_grades = self.calculator.recalculate_with_fixed_grade(
            all_exams, planned_exams, target_avg_scaled, exam_id, fixed_grade, 
            max_grade, self.required_grades)
            
        self.update_results_table()
    
    def update_results_table(self):
        """Update the results table with current required grades."""
        self.results_table.setRowCount(0)
        all_exams = self.db_manager.get_all_exams()
        planned_exams = self.db_manager.get_planned_exams()
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        
        if not planned_exams:
            self.summary_label.setText("Non ci sono esami pianificati per cui calcolare gli obiettivi.")
            return
            
        # Manual mode handling is different
        if self.mode == "manual":
            self._update_table_manual_mode(planned_exams, all_exams, max_grade)
            return
            
        # Calculate weighted average of required grades for summary (Auto mode)
        total_req_weighted_sum = 0
        total_req_credits = 0
        
        for exam in planned_exams:
            grade_value = self.required_grades.get(exam['id'], 0)
            if isinstance(grade_value, tuple):
                grade_value = grade_value[0]  # Extract grade from tuple
                
            total_req_weighted_sum += grade_value * exam['credits']
            total_req_credits += exam['credits']
            
        avg_required = total_req_weighted_sum / total_req_credits if total_req_credits > 0 else 0
        
        # Calculate projected final average
        passed_exams = [e for e in all_exams if e['status'] == 'passed']
        current_weighted_sum = sum(e['grade'] * e['credits'] for e in passed_exams)
        current_credits = sum(e['credits'] for e in passed_exams)
        
        total_weighted_sum = current_weighted_sum + total_req_weighted_sum
        total_credits = current_credits + total_req_credits
        
        projected_avg = total_weighted_sum / total_credits if total_credits > 0 else 0
        projected_avg_110 = (projected_avg / max_grade) * 110
        
        # Check if there are any fixed grades
        has_fixed_grades = any(isinstance(grade, tuple) for grade in self.required_grades.values())
        self.reset_button.setEnabled(has_fixed_grades)
        
        target_avg = self.target_avg_input.value()
        
        # Update summary text
        if has_fixed_grades:
            fixed_count = sum(1 for grade in self.required_grades.values() if isinstance(grade, tuple))
            self.summary_label.setText(
                f"Per raggiungere una media di {target_avg}/110 con {fixed_count} voti impostati manualmente, " +
                f"ti serve una media ponderata di {avg_required:.2f}/{max_grade} negli altri esami. " +
                f"Media finale prevista: {projected_avg_110:.2f}/110")
        else:
            self.summary_label.setText(
                f"Per raggiungere una media di {target_avg}/110, ti serve una media ponderata di " +
                f"{avg_required:.2f}/{max_grade} nei rimanenti esami. " +
                f"I voti suggeriti sono distribuiti in base ai CFU (esami con più CFU hanno voti target più bassi).")
        
        # Sort exams by credits (high to low) for clearer presentation
        sorted_exams = sorted(planned_exams, key=lambda e: e['credits'], reverse=True)
        self.exam_rows_map = []  # Map table rows to exam IDs
        
        # Fill the table with planned exams and their required grades
        for row, exam in enumerate(sorted_exams):
            self.results_table.insertRow(row)
            self.exam_rows_map.append((exam['id'], exam))  # Store mapping
            
            name_item = QTableWidgetItem(exam['name'])
            self.results_table.setItem(row, 0, name_item)
            
            credits_item = QTableWidgetItem(str(exam['credits']))
            credits_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 1, credits_item)
            
            # Get grade (could be a float or a tuple for fixed grades)
            grade_value = self.required_grades.get(exam['id'], 0)
            is_fixed = isinstance(grade_value, tuple)
            
            if is_fixed:
                actual_grade = grade_value[0]
                grade_text = f"{actual_grade:.1f} (fissato)"
            else:
                actual_grade = grade_value
                grade_text = f"{actual_grade:.2f}"
                
            grade_item = QTableWidgetItem(grade_text)
            grade_item.setTextAlignment(Qt.AlignCenter)
            
            # Use different styling for fixed vs calculated grades
            if is_fixed:
                # Fixed grade - use a different background color
                grade_item.setBackground(QColor(230, 230, 250))  # Light lavender
                grade_item.setForeground(QColor(0, 0, 139))      # Dark blue text
                font = grade_item.font()
                font.setBold(True)
                grade_item.setFont(font)
            else:
                # Calculated grade - color based on difficulty
                r = int(255 - (actual_grade / max_grade) * 55)  # Redder for lower grades (harder)
                g = int(200 + (actual_grade / max_grade) * 55)  # Greener for higher grades (easier)
                grade_item.setBackground(QColor(r, g, 200))
            
            self.results_table.setItem(row, 2, grade_item)
        
        # Add footer row with projected final average
        footer_row = self.results_table.rowCount()
        self.results_table.insertRow(footer_row)
        
        footer_item = QTableWidgetItem("Media finale prevista:")
        footer_item.setFont(QFont("", weight=QFont.Bold))
        self.results_table.setItem(footer_row, 0, footer_item)
        
        self.results_table.setItem(footer_row, 1, QTableWidgetItem(""))
        
        avg_item = QTableWidgetItem(f"{projected_avg_110:.2f}/110")
        avg_item.setFont(QFont("", weight=QFont.Bold))
        avg_item.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(footer_row, 2, avg_item)
            
        # Resize columns to contents
        self.results_table.resizeColumnsToContents()
        
    def _update_table_manual_mode(self, planned_exams, all_exams, max_grade):
        """Update the table in manual mode with spinners for direct grade editing."""
        # Sort exams by credits (high to low) for clearer presentation
        sorted_exams = sorted(planned_exams, key=lambda e: e['credits'], reverse=True)
        self.exam_rows_map = []  # Map table rows to exam IDs
        
        # Fill the table with planned exams and spinboxes for manual grade editing
        for row, exam in enumerate(sorted_exams):
            self.results_table.insertRow(row)
            self.exam_rows_map.append((exam['id'], exam))  # Store mapping
            
            # Name column
            name_item = QTableWidgetItem(exam['name'])
            self.results_table.setItem(row, 0, name_item)
            
            # Credits column
            credits_item = QTableWidgetItem(str(exam['credits']))
            credits_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 1, credits_item)
            
            # Grade column - use spinner for direct editing
            spinner = CustomGradeSpinBox(exam['id'])
            spinner.setMinimum(18)  # Minimum passing grade
            spinner.setMaximum(max_grade)
            spinner.setDecimals(1)
            spinner.setSingleStep(0.5)
            
            # Set current value from custom grades or calculated grades
            current_value = self.custom_grades.get(exam['id'], 0)
            spinner.setValue(current_value)
            
            # Connect signal to update projected average instantly
            spinner.valueModified.connect(self.on_custom_grade_changed)
            
            self.results_table.setCellWidget(row, 2, spinner)
        
        # Add footer row with projected final average
        footer_row = self.results_table.rowCount()
        self.results_table.insertRow(footer_row)
        
        footer_item = QTableWidgetItem("Media finale prevista:")
        footer_item.setFont(QFont("", weight=QFont.Bold))
        self.results_table.setItem(footer_row, 0, footer_item)
        
        self.results_table.setItem(footer_row, 1, QTableWidgetItem(""))
        
        # Calculate the projected average with custom grades
        passed_exams = [e for e in all_exams if e['status'] == 'passed']
        final_avg, final_avg_110 = self.calculator.calculate_final_average_with_custom_grades(
            passed_exams, planned_exams, self.custom_grades, max_grade)
        
        avg_item = QTableWidgetItem(f"{final_avg_110:.2f}/110")
        avg_item.setFont(QFont("", weight=QFont.Bold))
        avg_item.setTextAlignment(Qt.AlignCenter)
        self.results_table.setItem(footer_row, 2, avg_item)
        
        # Update summary text
        self.summary_label.setText(
            f"Con i voti impostati manualmente, la media finale prevista è {final_avg:.2f}/{max_grade} ({final_avg_110:.2f}/110)")
            
        # Resize columns to contents
        self.results_table.resizeColumnsToContents()
        
    def toggle_mode(self, checked):
        """Toggle between automatic and manual mode."""
        # Only respond to the radio button that was checked
        if not checked:
            return
            
        # Determine which mode is active
        new_mode = "manual" if self.manual_mode_radio.isChecked() else "auto"
        
        # If mode changed, update UI
        if new_mode != self.mode:
            self.mode = new_mode
            
            # Update visibility of instructions
            self.auto_instructions.setVisible(self.mode == "auto")
            self.manual_instructions.setVisible(self.mode == "manual")
            
            # Enable/disable calculate button and target input
            self.calc_button.setEnabled(self.mode == "auto")
            self.target_avg_input.setEnabled(self.mode == "auto")
            self.reset_button.setEnabled(self.mode == "auto" and any(isinstance(grade, tuple) for grade in self.required_grades.values()))
            
            # Initialize custom grades from current grades when switching to manual mode
            if self.mode == "manual":
                all_exams = self.db_manager.get_all_exams()
                planned_exams = self.db_manager.get_planned_exams()
                
                # Initialize with current calculated or fixed grades
                self.custom_grades = {}
                for exam in planned_exams:
                    grade_value = self.required_grades.get(exam['id'], 0)
                    if isinstance(grade_value, tuple):
                        self.custom_grades[exam['id']] = grade_value[0]
                    else:
                        self.custom_grades[exam['id']] = grade_value
            
            # Update the table display
            self.update_results_table()
    
    def on_custom_grade_changed(self, exam_id, new_value):
        """Handle changes to custom grade spinners in manual mode."""
        # Update the custom grade
        self.custom_grades[exam_id] = new_value
        
        # Update the table and summary to reflect the new grade
        self.update_manual_mode_summary()
        
    def update_manual_mode_summary(self):
        """Update the summary label with the projected average based on custom grades."""
        all_exams = self.db_manager.get_all_exams()
        planned_exams = self.db_manager.get_planned_exams()
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        
        # Get passed exams for current weight calculation
        passed_exams = [e for e in all_exams if e['status'] == 'passed']
        
        # Calculate final average with custom grades
        final_avg, final_avg_110 = self.calculator.calculate_final_average_with_custom_grades(
            passed_exams, planned_exams, self.custom_grades, max_grade)
            
        # Update summary text
        self.summary_label.setText(
            f"Con i voti impostati manualmente, la media finale prevista è {final_avg:.2f}/{max_grade} ({final_avg_110:.2f}/110)")
        
        # Find the footer row and update the average display
        footer_row = len(planned_exams)
        if footer_row < self.results_table.rowCount():
            avg_item = self.results_table.item(footer_row, 2)
            if avg_item:
                avg_item.setText(f"{final_avg_110:.2f}/110")
        
    def calculate_targets(self):
        """Calculate and display required grades to reach target average."""
        target_avg = self.target_avg_input.value()
        
        # Save target to settings
        self.db_manager.update_setting('target_average', str(target_avg))
        
        # Get all exams
        all_exams = self.db_manager.get_all_exams()
        planned_exams = self.db_manager.get_planned_exams()
        
        # Get max grade setting
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        
        # Convert target to max_grade scale
        target_avg_scaled = (target_avg / 110) * max_grade
        
        # Get fixed grades from existing calculations
        fixed_grades = {}
        for exam_id, grade in self.required_grades.items():
            if isinstance(grade, tuple):
                fixed_grades[exam_id] = grade[0]
        
        # Calculate required grades, preserving manually set grades
        if fixed_grades:
            self.required_grades = self.calculator.calculate_required_grades(
                all_exams, planned_exams, target_avg_scaled, max_grade, fixed_grades)
                
            # Mark fixed grades
            for exam_id, grade in fixed_grades.items():
                self.required_grades[exam_id] = (grade, True)
        else:
            # No fixed grades, calculate fresh
            self.required_grades = self.calculator.calculate_required_grades(
                all_exams, planned_exams, target_avg_scaled, max_grade)
        
        # Update results table with the new calculations
        self.update_results_table()


class CompletionPredictionWidget(QWidget):
    """Widget for displaying degree completion prediction."""
    
    def __init__(self, db_manager, calculator):
        super(CompletionPredictionWidget, self).__init__()
        self.db_manager = db_manager
        self.calculator = calculator
        self.prediction_data = None
        self.scenarios_data = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI for completion prediction."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Previsione di Completamento della Laurea")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Current pace section
        current_pace_group = QGroupBox("Previsione basata sul tuo ritmo attuale")
        current_pace_layout = QFormLayout()
        
        self.prediction_labels = {}
        
        # Labels for prediction information
        prediction_fields = [
            "Ritmo attuale:", "-- CFU al mese (-- esami al mese)",
            "Data prevista di completamento:", "--",
            "Tempo rimasto:", "-- mesi",
            "CFU rimasti:", "-- / --",
            "Esami rimasti:", "--"
        ]
        
        for i in range(0, len(prediction_fields), 2):
            label = QLabel(prediction_fields[i])
            value_label = QLabel(prediction_fields[i+1])
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Store value label for later updates
            self.prediction_labels[prediction_fields[i]] = value_label
            
            current_pace_layout.addRow(label, value_label)
            
        current_pace_group.setLayout(current_pace_layout)
        layout.addWidget(current_pace_group)
        
        # Alternative scenarios section
        scenarios_group = QGroupBox("Scenari alternativi")
        scenarios_layout = QGridLayout()
        
        # Headers
        headers = ["Ritmo", "Esami al mese", "Mesi rimanenti", "Data completamento"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setFont(QFont("", weight=QFont.Bold))
            scenarios_layout.addWidget(label, 0, col)
            
        # Scenario rows
        self.scenario_labels = {
            'slow_pace': {},
            'medium_pace': {},
            'fast_pace': {}
        }
        
        scenario_names = {
            'slow_pace': "Ritmo lento",
            'medium_pace': "Ritmo medio",
            'fast_pace': "Ritmo intenso"
        }
        
        for row, (scenario_key, scenario_name) in enumerate(scenario_names.items(), 1):
            # Scenario name
            name_label = QLabel(scenario_name)
            scenarios_layout.addWidget(name_label, row, 0)
            
            # Exams per month
            exams_label = QLabel("--")
            exams_label.setAlignment(Qt.AlignCenter)
            scenarios_layout.addWidget(exams_label, row, 1)
            self.scenario_labels[scenario_key]['exams_per_month'] = exams_label
            
            # Months remaining
            months_label = QLabel("--")
            months_label.setAlignment(Qt.AlignCenter)
            scenarios_layout.addWidget(months_label, row, 2)
            self.scenario_labels[scenario_key]['months_remaining'] = months_label
            
            # Completion date
            date_label = QLabel("--")
            date_label.setAlignment(Qt.AlignCenter)
            scenarios_layout.addWidget(date_label, row, 3)
            self.scenario_labels[scenario_key]['estimated_completion_date'] = date_label
            
        scenarios_group.setLayout(scenarios_layout)
        layout.addWidget(scenarios_group)
        
        # Note
        note_label = QLabel(
            "Nota: Queste previsioni sono basate sulle date degli esami sostenuti e sul numero "
            "di CFU rimanenti. La precisione dipende dalla regolarità con cui vengono sostenuti gli esami.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note_label)
        
        self.setLayout(layout)
        
    def update_prediction(self, passed_exams, planned_exams, total_credits_required):
        """Update the prediction with new data."""
        # Calculate base prediction
        self.prediction_data = self.calculator.calculate_completion_prediction(
            passed_exams, planned_exams, total_credits_required)
            
        # Calculate alternative scenarios
        self.scenarios_data = self.calculator.calculate_alternative_completion_scenarios(
            passed_exams, planned_exams, total_credits_required)
            
        # Update UI with prediction data
        self.update_prediction_display()
        
    def update_prediction_display(self):
        """Update the UI with the current prediction data."""
        # If no prediction data, show message and return
        if not self.prediction_data:
            for key, label in self.prediction_labels.items():
                if key == "Ritmo attuale:":
                    label.setText("Dati insufficienti per la previsione")
                else:
                    label.setText("--")
            return
            
        # Update current pace information
        pace_text = f"{self.prediction_data['pace_per_month']} CFU al mese ({self.prediction_data['exams_per_month']} esami al mese)"
        self.prediction_labels["Ritmo attuale:"].setText(pace_text)
        
        self.prediction_labels["Data prevista di completamento:"].setText(
            self.prediction_data['estimated_completion_date'])
            
        months_text = f"{self.prediction_data['months_remaining']} mesi"
        self.prediction_labels["Tempo rimasto:"].setText(months_text)
        
        total_required = int(self.db_manager.get_setting('total_credits', 180))
        credits_text = f"{int(self.prediction_data['credits_needed'])} / {total_required}"
        self.prediction_labels["CFU rimasti:"].setText(credits_text)
        
        exams_text = f"{self.prediction_data['exams_needed']}"
        self.prediction_labels["Esami rimasti:"].setText(exams_text)
        
        # Update alternative scenarios if available
        if self.scenarios_data:
            for scenario_key, scenario_data in self.scenarios_data.items():
                for data_key, value in scenario_data.items():
                    if data_key in self.scenario_labels[scenario_key]:
                        label = self.scenario_labels[scenario_key][data_key]
                        if data_key == 'exams_per_month':
                            label.setText(f"{value}")
                        elif data_key == 'months_remaining':
                            label.setText(f"{value} mesi")
                        else:  # estimated_completion_date
                            label.setText(f"{value}")


class AnalyticsWidget(QWidget):
    """Widget for academic analytics and projections."""
    
    def __init__(self, db_manager):
        super(AnalyticsWidget, self).__init__()
        self.db_manager = db_manager
        self.calculator = AcademicCalculator()
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the analytics UI."""
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Analisi Accademica")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Stats section
        stats_group = QGroupBox("Statistiche Accademiche")
        stats_layout = QGridLayout()
        
        # Labels for statistics
        labels = [
            "CFU Totali:", "0",
            "CFU Rimanenti:", "0",
            "Media Semplice:", "0.0",
            "Media Ponderata:", "0.0",
            "Media Semplice (110):", "0.0",
            "Media Ponderata (110):", "0.0"
        ]
        
        self.stat_labels = {}
        
        for i in range(0, len(labels), 2):
            row = i // 2
            
            label = QLabel(labels[i])
            value_label = QLabel(labels[i+1])
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Store value label for later updates
            self.stat_labels[labels[i]] = value_label
            
            stats_layout.addWidget(label, row, 0)
            stats_layout.addWidget(value_label, row, 1)
            
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # Create scrollable area for the rest of the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Grades trend chart
        self.trend_chart = LineChartWidget(self)
        scroll_layout.addWidget(self.trend_chart)
        
        # Target calculation widget
        self.target_widget = TargetCalculationWidget(self.db_manager, self.calculator)
        scroll_layout.addWidget(self.target_widget)
        
        # Completion prediction widget
        self.completion_widget = CompletionPredictionWidget(self.db_manager, self.calculator)
        scroll_layout.addWidget(self.completion_widget)
        
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
    @pyqtSlot()
    def refresh_data(self):
        """Refresh the analytics with the latest data."""
        # Get all exams
        all_exams = self.db_manager.get_all_exams()
        passed_exams = self.db_manager.get_passed_exams()
        
        # Get settings
        total_required_credits = int(self.db_manager.get_setting('total_credits', 180))
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        
        # Calculate statistics
        simple_avg = self.calculator.calculate_simple_average(all_exams)
        weighted_avg = self.calculator.calculate_weighted_average(all_exams)
        
        # Convert to 110 scale
        simple_avg_110 = self.calculator.convert_to_110_scale(simple_avg, max_grade)
        weighted_avg_110 = self.calculator.convert_to_110_scale(weighted_avg, max_grade)
        
        # Calculate credits
        earned_credits = self.calculator.calculate_total_credits(all_exams)
        remaining_credits = self.calculator.calculate_remaining_credits(all_exams, total_required_credits)
        
        # Update statistics labels
        self.stat_labels["CFU Totali:"].setText(f"{earned_credits}/{total_required_credits}")
        self.stat_labels["CFU Rimanenti:"].setText(str(remaining_credits))
        self.stat_labels["Media Semplice:"].setText(f"{simple_avg:.2f}/{max_grade}")
        self.stat_labels["Media Ponderata:"].setText(f"{weighted_avg:.2f}/{max_grade}")
        self.stat_labels["Media Semplice (110):"].setText(f"{simple_avg_110:.2f}/110")
        self.stat_labels["Media Ponderata (110):"].setText(f"{weighted_avg_110:.2f}/110")
        
        # Update trend chart
        self.trend_chart.update_chart(passed_exams, "Andamento Voti nel Tempo", f"Voto (max {max_grade})")
        
        # Refresh target calculations
        self.target_widget.calculate_targets()
        
        # Update completion prediction
        planned_exams = self.db_manager.get_planned_exams()
        self.completion_widget.update_prediction(passed_exams, planned_exams, total_required_credits)
