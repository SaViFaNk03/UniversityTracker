from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, 
    QComboBox, QDialog, QFormLayout, QLineEdit, QDateEdit, QTimeEdit, 
    QTextEdit, QCheckBox, QColorDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QMessageBox, QGroupBox, QSplitter, QFrame,
    QCalendarWidget, QMenu, QAction
)
from PyQt5.QtCore import Qt, QDate, QTime, QDateTime, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPalette, QIcon

import calendar
from datetime import datetime, timedelta

class AcademicCalendarWidget(QWidget):
    """Widget for academic calendar and exam scheduling."""
    
    # Signal emitted when an exam event is added or modified
    examUpdated = pyqtSignal()
    
    def __init__(self, db_manager):
        super(AcademicCalendarWidget, self).__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI for the academic calendar."""
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Calendario Accademico")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Calendar controls
        controls_layout = QHBoxLayout()
        
        # Month/Year navigation
        self.prev_month_btn = QPushButton("◀")
        self.prev_month_btn.setFixedWidth(40)
        self.prev_month_btn.clicked.connect(self.previous_month)
        
        self.month_year_label = QLabel()
        self.month_year_label.setAlignment(Qt.AlignCenter)
        month_year_font = self.month_year_label.font()
        month_year_font.setBold(True)
        self.month_year_label.setFont(month_year_font)
        
        self.next_month_btn = QPushButton("▶")
        self.next_month_btn.setFixedWidth(40)
        self.next_month_btn.clicked.connect(self.next_month)
        
        controls_layout.addWidget(self.prev_month_btn)
        controls_layout.addWidget(self.month_year_label)
        controls_layout.addWidget(self.next_month_btn)
        
        # Today button
        self.today_btn = QPushButton("Oggi")
        self.today_btn.clicked.connect(self.go_to_today)
        controls_layout.addWidget(self.today_btn)
        
        # Add event button
        self.add_event_btn = QPushButton("Aggiungi Evento")
        self.add_event_btn.clicked.connect(self.add_event)
        controls_layout.addWidget(self.add_event_btn)
        
        # Add session button
        self.add_session_btn = QPushButton("Aggiungi Sessione")
        self.add_session_btn.clicked.connect(self.add_academic_session)
        controls_layout.addWidget(self.add_session_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Splitter for calendar and events list
        splitter = QSplitter(Qt.Vertical)
        
        # Calendar grid
        calendar_frame = QFrame()
        calendar_layout = QVBoxLayout(calendar_frame)
        
        self.calendar_grid = QGridLayout()
        
        # Create day header row
        days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            header_font = label.font()
            header_font.setBold(True)
            label.setFont(header_font)
            self.calendar_grid.addWidget(label, 0, i)
        
        # Create empty day cells - will be filled in refresh_calendar
        self.day_cells = []
        for row in range(1, 7):  # Max 6 weeks in a month
            week_cells = []
            for col in range(7):  # 7 days in a week
                cell = DayCell(self)
                self.calendar_grid.addWidget(cell, row, col)
                week_cells.append(cell)
            self.day_cells.append(week_cells)
            
        calendar_layout.addLayout(self.calendar_grid)
        splitter.addWidget(calendar_frame)
        
        # Events for selected day
        events_frame = QFrame()
        events_layout = QVBoxLayout(events_frame)
        
        self.selected_day_label = QLabel("Eventi del Giorno")
        self.selected_day_label.setAlignment(Qt.AlignCenter)
        selected_day_font = self.selected_day_label.font()
        selected_day_font.setBold(True)
        self.selected_day_label.setFont(selected_day_font)
        events_layout.addWidget(self.selected_day_label)
        
        # Events table
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(5)
        self.events_table.setHorizontalHeaderLabels(["Ora", "Titolo", "Tipo", "Luogo", ""])
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.events_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.events_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        events_layout.addWidget(self.events_table)
        splitter.addWidget(events_frame)
        
        main_layout.addWidget(splitter)
        
        # Set the final layout
        self.setLayout(main_layout)
        
        # Initialize current date to today
        self.current_date = QDate.currentDate()
        
        # Refresh the calendar
        self.refresh_calendar()
        
    def refresh_calendar(self):
        """Refresh the calendar display for the current month."""
        # Update month/year label
        month_name = self.current_date.toString("MMMM")
        month_name = month_name[0].upper() + month_name[1:]  # Capitalize first letter
        year = self.current_date.year()
        self.month_year_label.setText(f"{month_name} {year}")
        
        # Get the first day of the month
        first_day = QDate(year, self.current_date.month(), 1)
        
        # Get the day of week for the first day (0 = Monday, 6 = Sunday in Qt)
        first_day_of_week = first_day.dayOfWeek() - 1  # Adjust to 0-based index
        
        # Calculate days in the month
        days_in_month = first_day.daysInMonth()
        
        # Get events for this month from database
        month_events = self.db_manager.get_events_for_month(year, self.current_date.month())
        
        # Get academic sessions that overlap with this month
        month_start = first_day.toString("yyyy-MM-dd")
        if self.current_date.month() == 12:
            month_end = QDate(year + 1, 1, 1).toString("yyyy-MM-dd")
        else:
            month_end = QDate(year, self.current_date.month() + 1, 1).toString("yyyy-MM-dd")
            
        academic_sessions = self.db_manager.get_calendar_events(
            start_date=month_start, 
            end_date=month_end,
            event_type="academic_session"
        )
        
        # Group events by day
        events_by_day = {}
        for event in month_events:
            event_date = QDate.fromString(event['start_date'].split('T')[0], "yyyy-MM-dd")
            day = event_date.day()
            
            if day not in events_by_day:
                events_by_day[day] = []
                
            events_by_day[day].append(event)
            
        # Clear all day cells
        for week in self.day_cells:
            for cell in week:
                cell.clear()
                
        # Fill in the days
        day = 1
        for week_idx in range(6):  # 6 possible weeks in a view
            for day_idx in range(7):  # 7 days in a week
                if (week_idx == 0 and day_idx < first_day_of_week) or (day > days_in_month):
                    # Empty cell (previous/next month)
                    self.day_cells[week_idx][day_idx].setVisible(False)
                else:
                    # Set up the day cell
                    cell = self.day_cells[week_idx][day_idx]
                    cell.setVisible(True)
                    cell.setup(year, self.current_date.month(), day)
                    
                    # Add events for this day
                    if day in events_by_day:
                        cell.add_events(events_by_day[day])
                    
                    # Highlight today
                    today = QDate.currentDate()
                    if (year == today.year() and 
                        self.current_date.month() == today.month() and 
                        day == today.day()):
                        cell.highlight_as_today()
                        
                    # Check for academic sessions
                    for session in academic_sessions:
                        session_start = QDate.fromString(session['start_date'].split('T')[0], "yyyy-MM-dd")
                        session_end = QDate.fromString(session['end_date'].split('T')[0], "yyyy-MM-dd")
                        current_date = QDate(year, self.current_date.month(), day)
                        
                        if session_start <= current_date <= session_end:
                            cell.mark_as_session(session['color'])
                    
                    day += 1
                    
        # Update events for the currently selected date, if any
        if hasattr(self, 'selected_date'):
            self.show_events_for_date(self.selected_date)
                    
    def previous_month(self):
        """Navigate to the previous month."""
        new_month = self.current_date.month() - 1
        new_year = self.current_date.year()
        
        if new_month < 1:
            new_month = 12
            new_year -= 1
            
        self.current_date = QDate(new_year, new_month, 1)
        self.refresh_calendar()
        
    def next_month(self):
        """Navigate to the next month."""
        new_month = self.current_date.month() + 1
        new_year = self.current_date.year()
        
        if new_month > 12:
            new_month = 1
            new_year += 1
            
        self.current_date = QDate(new_year, new_month, 1)
        self.refresh_calendar()
        
    def go_to_today(self):
        """Navigate to the current month and highlight today."""
        self.current_date = QDate.currentDate()
        self.refresh_calendar()
        
        # Select today's cell
        self.selected_date = self.current_date
        self.show_events_for_date(self.selected_date)
        
    def add_event(self):
        """Open dialog to add a new calendar event."""
        dialog = EventDialog(self.db_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_calendar()
            
    def add_academic_session(self):
        """Open dialog to add a new academic session."""
        dialog = AcademicSessionDialog(self.db_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_calendar()
            
    def show_events_for_date(self, date):
        """Show events for the selected date in the events table."""
        self.selected_date = date
        
        # Update the selected day label
        day_name = date.toString("dddd")
        day_name = day_name[0].upper() + day_name[1:]  # Capitalize first letter
        self.selected_day_label.setText(f"Eventi del {day_name} {date.day()} {date.toString('MMMM yyyy')}")
        
        # Get events for this date
        start_date = date.toString("yyyy-MM-dd")
        end_date = date.addDays(1).toString("yyyy-MM-dd")
        events = self.db_manager.get_calendar_events(start_date=start_date, end_date=end_date)
        
        # Clear and set up the events table
        self.events_table.setRowCount(0)
        
        if not events:
            self.events_table.setRowCount(1)
            no_events = QTableWidgetItem("Nessun evento per questa data")
            no_events.setTextAlignment(Qt.AlignCenter)
            self.events_table.setSpan(0, 0, 1, 5)
            self.events_table.setItem(0, 0, no_events)
            return
            
        # Add each event to the table
        for row, event in enumerate(events):
            self.events_table.insertRow(row)
            
            # Time column
            if event['all_day']:
                time_item = QTableWidgetItem("Tutto il giorno")
            else:
                start_time = QDateTime.fromString(event['start_date'], Qt.ISODate).time().toString("HH:mm")
                end_time = QDateTime.fromString(event['end_date'], Qt.ISODate).time().toString("HH:mm")
                time_item = QTableWidgetItem(f"{start_time} - {end_time}")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.events_table.setItem(row, 0, time_item)
            
            # Title column
            title_item = QTableWidgetItem(event['title'])
            self.events_table.setItem(row, 1, title_item)
            
            # Event type column
            type_item = QTableWidgetItem(self.get_event_type_display(event['event_type']))
            self.events_table.setItem(row, 2, type_item)
            
            # Location column
            location = event['location'] if event['location'] else "N/A"
            location_item = QTableWidgetItem(location)
            self.events_table.setItem(row, 3, location_item)
            
            # Actions column
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("🖉")
            edit_btn.setFixedSize(24, 24)
            edit_btn.setToolTip("Modifica evento")
            edit_btn.clicked.connect(lambda _, e=event: self.edit_event(e))
            
            delete_btn = QPushButton("🗑")
            delete_btn.setFixedSize(24, 24)
            delete_btn.setToolTip("Elimina evento")
            delete_btn.clicked.connect(lambda _, e=event: self.delete_event(e))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.events_table.setCellWidget(row, 4, actions_widget)
            
        # Resize rows to content
        self.events_table.resizeRowsToContents()
        
    def edit_event(self, event):
        """Open dialog to edit an existing event."""
        dialog = EventDialog(self.db_manager, event=event, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_calendar()
            self.show_events_for_date(self.selected_date)
            
    def delete_event(self, event):
        """Delete an event after confirmation."""
        confirm = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare l'evento '{event['title']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.db_manager.delete_calendar_event(event['id'])
            self.refresh_calendar()
            self.show_events_for_date(self.selected_date)
            
            # If the event was linked to an exam, also emit the examUpdated signal
            if event['exam_id']:
                self.examUpdated.emit()
    
    def get_event_type_display(self, event_type):
        """Convert event type to a display name."""
        event_types = {
            'exam': 'Esame',
            'study': 'Studio',
            'deadline': 'Scadenza',
            'meeting': 'Incontro',
            'session': 'Sessione',
            'holiday': 'Vacanza',
            'other': 'Altro'
        }
        return event_types.get(event_type, event_type.capitalize())


class DayCell(QFrame):
    """A cell representing a day in the calendar."""
    
    def __init__(self, parent):
        super(DayCell, self).__init__(parent)
        self.parent_widget = parent
        self.date = None
        self.is_today = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI for the day cell."""
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)
        
        # Day number
        self.day_label = QLabel()
        self.day_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(self.day_label)
        
        # Event indicators container
        self.events_layout = QVBoxLayout()
        self.events_layout.setContentsMargins(0, 0, 0, 0)
        self.events_layout.setSpacing(1)
        layout.addLayout(self.events_layout)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Set minimum size
        self.setMinimumSize(100, 80)
        
        # Default style
        self.set_default_style()
        
    def set_default_style(self):
        """Set the default style for the cell."""
        self.setStyleSheet("""
        DayCell {
            background-color: white;
            border: 1px solid #ccc;
        }
        """)
        
    def setup(self, year, month, day):
        """Set up the cell for a specific date."""
        self.date = QDate(year, month, day)
        self.day_label.setText(str(day))
        
        # Clear any previous events
        self.clear_events()
        
        # Reset styles
        self.set_default_style()
        self.is_today = False
        
    def clear(self):
        """Clear the cell completely."""
        self.day_label.setText("")
        self.clear_events()
        self.set_default_style()
        self.is_today = False
        
    def highlight_as_today(self):
        """Highlight this cell as today."""
        self.is_today = True
        self.setStyleSheet("""
        DayCell {
            background-color: #e6f7ff;
            border: 1px solid #1890ff;
        }
        """)
        
    def mark_as_session(self, color=None):
        """Mark this cell as part of an academic session."""
        bg_color = color if color else "#fff7e6"
        
        # Don't override today's highlighting
        if not self.is_today:
            self.setStyleSheet(f"""
            DayCell {{
                background-color: {bg_color};
                border: 1px solid #d9d9d9;
            }}
            """)
        
    def clear_events(self):
        """Clear all event indicators."""
        # Remove all widgets from events layout
        while self.events_layout.count():
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def add_events(self, events):
        """Add event indicators to the cell."""
        # Maximum number of events to show directly
        max_shown_events = 3
        
        # Group events by type
        event_types = {}
        for event in events:
            event_type = event['event_type']
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event)
            
        # Add indicator for each event type, up to max_shown_events
        shown_count = 0
        for event_type, type_events in event_types.items():
            if shown_count >= max_shown_events:
                break
                
            # Create indicator
            color = self.get_color_for_event_type(event_type)
            indicator = QLabel(f"{len(type_events)} {self.get_event_type_short(event_type)}")
            indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 2px;
            padding: 1px 3px;
            color: white;
            font-size: 8pt;
            """)
            
            self.events_layout.addWidget(indicator)
            shown_count += 1
            
        # If there are more events than we can show, add a "more" indicator
        if sum(len(events) for events in event_types.values()) > shown_count:
            more_indicator = QLabel("...")
            more_indicator.setStyleSheet("""
            color: #888;
            font-size: 8pt;
            font-weight: bold;
            """)
            self.events_layout.addWidget(more_indicator)
            
    def get_color_for_event_type(self, event_type):
        """Get a color for event type."""
        colors = {
            'exam': "#f5222d",  # Red
            'study': "#1890ff",  # Blue
            'deadline': "#fa8c16",  # Orange
            'meeting': "#722ed1",  # Purple
            'session': "#52c41a",  # Green
            'holiday': "#eb2f96",  # Pink
            'other': "#595959"   # Grey
        }
        return colors.get(event_type, "#595959")
        
    def get_event_type_short(self, event_type):
        """Get short display name for event type."""
        short_names = {
            'exam': "Esami",
            'study': "Studio",
            'deadline': "Scad.",
            'meeting': "Incontri",
            'session': "Sess.",
            'holiday': "Vacanza",
            'other': "Altri"
        }
        return short_names.get(event_type, event_type.capitalize())
        
    def mouseReleaseEvent(self, event):
        """Handle mouse click to show events for this day."""
        if self.date:
            self.parent_widget.show_events_for_date(self.date)
        super(DayCell, self).mouseReleaseEvent(event)


class EventDialog(QDialog):
    """Dialog for adding/editing calendar events."""
    
    def __init__(self, db_manager, event=None, exam_id=None, parent=None):
        super(EventDialog, self).__init__(parent)
        self.db_manager = db_manager
        self.event = event  # None for new events, event dict for editing
        self.exam_id = exam_id  # For pre-filling exam info, only used for new events
        
        self.setWindowTitle("Aggiungi Evento" if not event else "Modifica Evento")
        self.resize(500, 400)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI for the event dialog."""
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Title field
        self.title_edit = QLineEdit()
        form_layout.addRow("Titolo:", self.title_edit)
        
        # Event type selection
        self.type_combo = QComboBox()
        event_types = [
            ('exam', 'Esame'),
            ('study', 'Studio'),
            ('deadline', 'Scadenza'),
            ('meeting', 'Incontro'),
            ('session', 'Sessione'),
            ('holiday', 'Vacanza'),
            ('other', 'Altro')
        ]
        for value, display in event_types:
            self.type_combo.addItem(display, value)
        form_layout.addRow("Tipo:", self.type_combo)
        
        # Exam selection (only for exam events)
        self.exam_group = QGroupBox("Associa a Esame")
        self.exam_group.setCheckable(True)
        self.exam_group.setChecked(False)
        
        exam_layout = QFormLayout()
        self.exam_combo = QComboBox()
        self.load_planned_exams()
        exam_layout.addRow("Esame:", self.exam_combo)
        self.exam_group.setLayout(exam_layout)
        form_layout.addRow(self.exam_group)
        
        # Connect type change to enable/disable exam selection
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        
        # All day checkbox
        self.all_day_check = QCheckBox("Tutto il giorno")
        self.all_day_check.setChecked(True)
        self.all_day_check.stateChanged.connect(self.on_all_day_changed)
        form_layout.addRow("", self.all_day_check)
        
        # Date selection
        date_layout = QHBoxLayout()
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Data inizio:"))
        date_layout.addWidget(self.start_date_edit)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Data fine:"))
        date_layout.addWidget(self.end_date_edit)
        
        form_layout.addRow("", date_layout)
        
        # Time selection (for non-all-day events)
        time_layout = QHBoxLayout()
        
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(9, 0))
        self.start_time_edit.setEnabled(False)
        time_layout.addWidget(QLabel("Ora inizio:"))
        time_layout.addWidget(self.start_time_edit)
        
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(10, 0))
        self.end_time_edit.setEnabled(False)
        time_layout.addWidget(QLabel("Ora fine:"))
        time_layout.addWidget(self.end_time_edit)
        
        form_layout.addRow("", time_layout)
        
        # Location
        self.location_edit = QLineEdit()
        form_layout.addRow("Luogo:", self.location_edit)
        
        # Color selection
        color_layout = QHBoxLayout()
        self.color_edit = QLineEdit()
        self.color_edit.setReadOnly(True)
        self.color_edit.setText("#1890ff")  # Default blue
        self.color_edit.setStyleSheet("background-color: #1890ff; color: white;")
        
        self.color_btn = QPushButton("Seleziona")
        self.color_btn.clicked.connect(self.select_color)
        
        color_layout.addWidget(self.color_edit)
        color_layout.addWidget(self.color_btn)
        form_layout.addRow("Colore:", color_layout)
        
        # Description
        self.description_edit = QTextEdit()
        form_layout.addRow("Descrizione:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Annulla")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Salva")
        self.save_btn.clicked.connect(self.save_event)
        self.save_btn.setDefault(True)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # If editing, populate fields
        if self.event:
            self.populate_event_data()
        elif self.exam_id:
            self.populate_from_exam()
            
        # Initial type check
        self.on_type_changed()
        
    def load_planned_exams(self):
        """Load planned exams into the combo box."""
        self.exam_combo.clear()
        
        # Add empty option
        self.exam_combo.addItem("Seleziona un esame...", None)
        
        # Get planned exams
        planned_exams = self.db_manager.get_planned_exams()
        
        for exam in planned_exams:
            self.exam_combo.addItem(f"{exam['name']} ({exam['credits']} CFU)", exam['id'])
            
    def on_type_changed(self):
        """Handle event type change."""
        current_type = self.type_combo.currentData()
        
        # Enable exam selection only for exam events
        self.exam_group.setEnabled(current_type == 'exam')
        
        # If switched away from exam type, uncheck exam association
        if current_type != 'exam':
            self.exam_group.setChecked(False)
        else:
            self.exam_group.setChecked(True)
            
    def on_all_day_changed(self, state):
        """Handle all-day checkbox change."""
        is_all_day = state == Qt.Checked
        self.start_time_edit.setEnabled(not is_all_day)
        self.end_time_edit.setEnabled(not is_all_day)
        
    def select_color(self):
        """Open color dialog for selection."""
        current_color = QColor(self.color_edit.text())
        color = QColorDialog.getColor(current_color, self, "Seleziona colore")
        
        if color.isValid():
            self.color_edit.setText(color.name())
            self.color_edit.setStyleSheet(f"background-color: {color.name()}; color: white;")
            
    def populate_event_data(self):
        """Populate dialog fields from existing event data."""
        # Title
        self.title_edit.setText(self.event['title'])
        
        # Type
        type_index = self.type_combo.findData(self.event['event_type'])
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
            
        # Exam association
        if self.event['exam_id']:
            self.exam_group.setChecked(True)
            exam_index = self.exam_combo.findData(self.event['exam_id'])
            if exam_index >= 0:
                self.exam_combo.setCurrentIndex(exam_index)
                
        # All day
        is_all_day = bool(self.event['all_day'])
        self.all_day_check.setChecked(is_all_day)
        
        # Dates and times
        start_dt = QDateTime.fromString(self.event['start_date'], Qt.ISODate)
        end_dt = QDateTime.fromString(self.event['end_date'], Qt.ISODate)
        
        self.start_date_edit.setDate(start_dt.date())
        self.end_date_edit.setDate(end_dt.date())
        
        if not is_all_day:
            self.start_time_edit.setTime(start_dt.time())
            self.end_time_edit.setTime(end_dt.time())
            
        # Location
        if self.event['location']:
            self.location_edit.setText(self.event['location'])
            
        # Color
        if self.event['color']:
            self.color_edit.setText(self.event['color'])
            self.color_edit.setStyleSheet(f"background-color: {self.event['color']}; color: white;")
            
        # Description
        if self.event['description']:
            self.description_edit.setText(self.event['description'])
            
    def populate_from_exam(self):
        """Pre-fill fields when creating an event for a specific exam."""
        # Get exam data
        exam = self.db_manager.get_exam(self.exam_id)
        if not exam:
            return
            
        # Set title
        self.title_edit.setText(f"Esame: {exam['name']}")
        
        # Set type to 'exam'
        type_index = self.type_combo.findData('exam')
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
            
        # Select exam
        self.exam_group.setChecked(True)
        exam_index = self.exam_combo.findData(exam['id'])
        if exam_index >= 0:
            self.exam_combo.setCurrentIndex(exam_index)
            
        # If exam has a date, use it
        if exam['date']:
            try:
                exam_date = QDate.fromString(exam['date'], "yyyy-MM-dd")
                if exam_date.isValid():
                    self.start_date_edit.setDate(exam_date)
                    self.end_date_edit.setDate(exam_date)
            except:
                pass  # Use default date if parsing fails
                
    def save_event(self):
        """Save the event data to the database."""
        # Validate inputs
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Dati Mancanti", "Inserisci un titolo per l'evento.")
            return
            
        # Get event data
        event_type = self.type_combo.currentData()
        
        # Exam association
        exam_id = None
        if self.exam_group.isChecked() and event_type == 'exam':
            exam_id = self.exam_combo.currentData()
            
        # Date and time
        is_all_day = self.all_day_check.isChecked()
        
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        
        if is_all_day:
            start_datetime = QDateTime(start_date, QTime(0, 0))
            end_datetime = QDateTime(end_date, QTime(23, 59, 59))
        else:
            start_time = self.start_time_edit.time()
            end_time = self.end_time_edit.time()
            
            start_datetime = QDateTime(start_date, start_time)
            end_datetime = QDateTime(end_date, end_time)
            
        # Validate dates
        if start_datetime > end_datetime:
            QMessageBox.warning(self, "Data non valida", "La data di inizio deve essere precedente alla data di fine.")
            return
            
        # Other fields
        location = self.location_edit.text().strip()
        color = self.color_edit.text()
        description = self.description_edit.toPlainText().strip()
        
        # Save the event
        if self.event:  # Update existing
            success = self.db_manager.update_calendar_event(
                self.event['id'],
                title=title,
                event_type=event_type,
                start_date=start_datetime.toString(Qt.ISODate),
                end_date=end_datetime.toString(Qt.ISODate),
                exam_id=exam_id,
                all_day=is_all_day,
                location=location or None,
                description=description or None,
                color=color
            )
        else:  # Create new
            self.db_manager.add_calendar_event(
                title=title,
                event_type=event_type,
                start_date=start_datetime.toString(Qt.ISODate),
                end_date=end_datetime.toString(Qt.ISODate),
                exam_id=exam_id,
                all_day=is_all_day,
                location=location or None,
                description=description or None,
                color=color
            )
            success = True
            
        if success:
            # If this was an exam event, update the exam date if needed
            if exam_id and event_type == 'exam':
                self.db_manager.update_exam(
                    exam_id,
                    date=start_date.toString("yyyy-MM-dd")
                )
                # Emit signal that an exam was updated
                if self.parent():
                    self.parent().examUpdated.emit()
                    
            self.accept()
        else:
            QMessageBox.warning(self, "Errore", "Si è verificato un errore durante il salvataggio dell'evento.")


class AcademicSessionDialog(QDialog):
    """Dialog for adding/editing academic sessions."""
    
    def __init__(self, db_manager, session=None, parent=None):
        super(AcademicSessionDialog, self).__init__(parent)
        self.db_manager = db_manager
        self.session = session  # None for new sessions, session dict for editing
        
        self.setWindowTitle("Aggiungi Sessione Accademica" if not session else "Modifica Sessione")
        self.resize(450, 350)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI for the session dialog."""
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        form_layout.addRow("Nome:", self.name_edit)
        
        # Date selection
        date_layout = QHBoxLayout()
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Data inizio:"))
        date_layout.addWidget(self.start_date_edit)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(30))  # Default to 1 month duration
        date_layout.addWidget(QLabel("Data fine:"))
        date_layout.addWidget(self.end_date_edit)
        
        form_layout.addRow("", date_layout)
        
        # Color selection
        color_layout = QHBoxLayout()
        self.color_edit = QLineEdit()
        self.color_edit.setReadOnly(True)
        self.color_edit.setText("#fff7e6")  # Default light orange
        self.color_edit.setStyleSheet("background-color: #fff7e6; color: black;")
        
        self.color_btn = QPushButton("Seleziona")
        self.color_btn.clicked.connect(self.select_color)
        
        color_layout.addWidget(self.color_edit)
        color_layout.addWidget(self.color_btn)
        form_layout.addRow("Colore:", color_layout)
        
        # Description
        self.description_edit = QTextEdit()
        form_layout.addRow("Descrizione:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Annulla")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Salva")
        self.save_btn.clicked.connect(self.save_session)
        self.save_btn.setDefault(True)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # If editing, populate fields
        if self.session:
            self.populate_session_data()
            
    def select_color(self):
        """Open color dialog for selection."""
        current_color = QColor(self.color_edit.text())
        color = QColorDialog.getColor(current_color, self, "Seleziona colore")
        
        if color.isValid():
            self.color_edit.setText(color.name())
            # Use appropriate text color for readability
            text_color = "white" if color.lightness() < 128 else "black"
            self.color_edit.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")
            
    def populate_session_data(self):
        """Populate dialog fields from existing session data."""
        # Name
        self.name_edit.setText(self.session['name'])
        
        # Dates
        start_date = QDate.fromString(self.session['start_date'].split('T')[0], "yyyy-MM-dd")
        end_date = QDate.fromString(self.session['end_date'].split('T')[0], "yyyy-MM-dd")
        
        if start_date.isValid():
            self.start_date_edit.setDate(start_date)
        if end_date.isValid():
            self.end_date_edit.setDate(end_date)
            
        # Color
        if self.session['color']:
            self.color_edit.setText(self.session['color'])
            # Use appropriate text color for readability
            color = QColor(self.session['color'])
            text_color = "white" if color.lightness() < 128 else "black"
            self.color_edit.setStyleSheet(f"background-color: {self.session['color']}; color: {text_color};")
            
        # Description
        if self.session['description']:
            self.description_edit.setText(self.session['description'])
            
    def save_session(self):
        """Save the session data to the database."""
        # Validate inputs
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Dati Mancanti", "Inserisci un nome per la sessione accademica.")
            return
            
        # Dates
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        
        # Validate dates
        if start_date > end_date:
            QMessageBox.warning(self, "Data non valida", "La data di inizio deve essere precedente alla data di fine.")
            return
            
        # Other fields
        color = self.color_edit.text()
        description = self.description_edit.toPlainText().strip()
        
        # Create calendar event for the session
        start_datetime = QDateTime(start_date, QTime(0, 0)).toString(Qt.ISODate)
        end_datetime = QDateTime(end_date, QTime(23, 59, 59)).toString(Qt.ISODate)
        
        # Save as a special calendar event of type "academic_session"
        if self.session:  # Update existing
            success = self.db_manager.update_calendar_event(
                self.session['id'],
                title=name,
                event_type="academic_session",
                start_date=start_datetime,
                end_date=end_datetime,
                all_day=True,
                description=description or None,
                color=color
            )
        else:  # Create new
            self.db_manager.add_calendar_event(
                title=name,
                event_type="academic_session",
                start_date=start_datetime,
                end_date=end_datetime,
                all_day=True,
                description=description or None,
                color=color
            )
            success = True
            
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "Errore", "Si è verificato un errore durante il salvataggio della sessione.")