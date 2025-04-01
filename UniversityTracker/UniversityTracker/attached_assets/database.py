import os
import sqlite3
from datetime import datetime

class DatabaseManager:
    """Manages all database operations for the University Career Manager."""
    
    def __init__(self, db_path=None):
        """Initialize database connection and create tables if they don't exist."""
        if db_path is None:
            # Use user's documents folder for database storage
            documents_folder = os.path.join(os.path.expanduser("~"), "Documents")
            app_folder = os.path.join(documents_folder, "UniversityCareerManager")
            
            # Create app folder if it doesn't exist
            if not os.path.exists(app_folder):
                os.makedirs(app_folder)
                
            db_path = os.path.join(app_folder, "university_career.db")
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self._create_tables()
        
    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        # Exams table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            credits INTEGER NOT NULL,
            grade INTEGER,
            status TEXT NOT NULL,
            date TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Settings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        # Calendar events table for exam scheduling
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            title TEXT NOT NULL,
            event_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            all_day INTEGER NOT NULL DEFAULT 1,
            location TEXT,
            description TEXT,
            color TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
        )
        ''')
        
        # Academic sessions table for storing exam periods
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS academic_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            color TEXT,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Insert default settings if they don't exist
        default_settings = [
            ('degree_name', 'Computer Science'),
            ('total_credits', '180'),
            ('target_average', '100'),
            ('max_grade', '30'),
            ('pass_threshold', '18')
        ]
        
        for key, value in default_settings:
            self.cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value)
            VALUES (?, ?)
            ''', (key, value))
            
        self.conn.commit()
        
    def add_exam(self, name, credits, grade=None, status="planned", date=None, notes=None):
        """
        Add a new exam to the database.
        
        Args:
            name (str): Name of the exam
            credits (int): Number of credits for the exam
            grade (int, optional): Grade received (if passed)
            status (str): Status of the exam ('passed', 'failed', 'planned')
            date (str, optional): Date of the exam (YYYY-MM-DD)
            notes (str, optional): Additional notes
            
        Returns:
            int: ID of the newly added exam
        """
        now = datetime.now().isoformat()
        
        self.cursor.execute('''
        INSERT INTO exams (name, credits, grade, status, date, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, credits, grade, status, date, notes, now, now))
        
        self.conn.commit()
        return self.cursor.lastrowid
        
    def update_exam(self, exam_id, name=None, credits=None, grade=None, status=None, date=None, notes=None):
        """
        Update an existing exam in the database.
        
        Args:
            exam_id (int): ID of the exam to update
            name (str, optional): New name
            credits (int, optional): New credits value
            grade (int, optional): New grade
            status (str, optional): New status
            date (str, optional): New date
            notes (str, optional): New notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get current values
        self.cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
        exam = self.cursor.fetchone()
        
        if not exam:
            return False
            
        # Use current values if new ones not provided
        name = name if name is not None else exam['name']
        credits = credits if credits is not None else exam['credits']
        grade = grade if grade is not None else exam['grade']
        status = status if status is not None else exam['status']
        date = date if date is not None else exam['date']
        notes = notes if notes is not None else exam['notes']
        updated_at = datetime.now().isoformat()
        
        self.cursor.execute('''
        UPDATE exams
        SET name = ?, credits = ?, grade = ?, status = ?, date = ?, notes = ?, updated_at = ?
        WHERE id = ?
        ''', (name, credits, grade, status, date, notes, updated_at, exam_id))
        
        self.conn.commit()
        return True
        
    def delete_exam(self, exam_id):
        """
        Delete an exam from the database.
        
        Args:
            exam_id (int): ID of the exam to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
        
    def get_exam(self, exam_id):
        """
        Get a single exam by ID.
        
        Args:
            exam_id (int): ID of the exam
            
        Returns:
            dict: Exam data or None if not found
        """
        self.cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
        exam = self.cursor.fetchone()
        return dict(exam) if exam else None
        
    def get_all_exams(self, status=None):
        """
        Get all exams, optionally filtered by status.
        
        Args:
            status (str, optional): Filter by status ('passed', 'failed', 'planned')
            
        Returns:
            list: List of exam dictionaries
        """
        if status:
            self.cursor.execute("SELECT * FROM exams WHERE status = ? ORDER BY date DESC", (status,))
        else:
            self.cursor.execute("SELECT * FROM exams ORDER BY date DESC")
            
        return [dict(row) for row in self.cursor.fetchall()]
        
    def get_passed_exams(self):
        """Get all passed exams."""
        return self.get_all_exams('passed')
        
    def get_failed_exams(self):
        """Get all failed exams."""
        return self.get_all_exams('failed')
        
    def get_planned_exams(self):
        """Get all planned exams."""
        return self.get_all_exams('planned')
        
    def get_setting(self, key, default=None):
        """
        Get a setting value by key.
        
        Args:
            key (str): Setting key
            default: Default value if setting not found
            
        Returns:
            str: Setting value or default
        """
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        
        if result:
            return result['value']
        return default
        
    def update_setting(self, key, value):
        """
        Update a setting value.
        
        Args:
            key (str): Setting key
            value (str): New value
            
        Returns:
            bool: True if successful
        """
        self.cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
        ''', (key, value))
        
        self.conn.commit()
        return True
        
    def get_total_credits(self):
        """Get total credits earned from passed exams."""
        self.cursor.execute("""
        SELECT SUM(credits) as total_credits
        FROM exams
        WHERE status = 'passed'
        """)
        
        result = self.cursor.fetchone()
        return result['total_credits'] if result and result['total_credits'] else 0
        
    def get_total_exams_count(self, status=None):
        """Get count of exams, optionally filtered by status."""
        if status:
            self.cursor.execute("SELECT COUNT(*) as count FROM exams WHERE status = ?", (status,))
        else:
            self.cursor.execute("SELECT COUNT(*) as count FROM exams")
            
        result = self.cursor.fetchone()
        return result['count'] if result else 0
    
    # Calendar event methods
    def add_calendar_event(self, title, event_type, start_date, end_date, exam_id=None, 
                         all_day=True, location=None, description=None, color=None):
        """
        Add a new calendar event.
        
        Args:
            title (str): Event title
            event_type (str): Type of event ('exam', 'study', 'deadline', etc.)
            start_date (str): Start date and time (ISO format)
            end_date (str): End date and time (ISO format)
            exam_id (int, optional): Associated exam ID
            all_day (bool): Whether the event is all-day
            location (str, optional): Event location
            description (str, optional): Event description
            color (str, optional): Event color (hex code)
            
        Returns:
            int: ID of the newly added event
        """
        now = datetime.now().isoformat()
        
        self.cursor.execute('''
        INSERT INTO calendar_events (exam_id, title, event_type, start_date, end_date,
                                     all_day, location, description, color, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (exam_id, title, event_type, start_date, end_date, 
              1 if all_day else 0, location, description, color, now, now))
        
        self.conn.commit()
        return self.cursor.lastrowid
        
    def update_calendar_event(self, event_id, title=None, event_type=None, start_date=None, 
                            end_date=None, exam_id=None, all_day=None, location=None, 
                            description=None, color=None):
        """
        Update an existing calendar event.
        
        Args:
            event_id (int): ID of the event to update
            [other args same as add_calendar_event]
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get current values
        self.cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        event = self.cursor.fetchone()
        
        if not event:
            return False
            
        # Use current values if new ones not provided
        title = title if title is not None else event['title']
        event_type = event_type if event_type is not None else event['event_type']
        start_date = start_date if start_date is not None else event['start_date']
        end_date = end_date if end_date is not None else event['end_date']
        exam_id = exam_id if exam_id is not None else event['exam_id']
        all_day = all_day if all_day is not None else event['all_day']
        location = location if location is not None else event['location']
        description = description if description is not None else event['description']
        color = color if color is not None else event['color']
        updated_at = datetime.now().isoformat()
        
        self.cursor.execute('''
        UPDATE calendar_events
        SET title = ?, event_type = ?, start_date = ?, end_date = ?, exam_id = ?,
            all_day = ?, location = ?, description = ?, color = ?, updated_at = ?
        WHERE id = ?
        ''', (title, event_type, start_date, end_date, exam_id,
              1 if all_day else 0, location, description, color, updated_at, event_id))
        
        self.conn.commit()
        return True
        
    def delete_calendar_event(self, event_id):
        """
        Delete a calendar event.
        
        Args:
            event_id (int): ID of the event to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
        
    def get_calendar_event(self, event_id):
        """
        Get a single calendar event by ID.
        
        Args:
            event_id (int): ID of the event
            
        Returns:
            dict: Event data or None if not found
        """
        self.cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
        
    def get_calendar_events(self, start_date=None, end_date=None, event_type=None, exam_id=None):
        """
        Get calendar events with optional filtering.
        
        Args:
            start_date (str, optional): Filter events starting from this date
            end_date (str, optional): Filter events ending before this date
            event_type (str, optional): Filter by event type
            exam_id (int, optional): Filter by associated exam
            
        Returns:
            list: List of event dictionaries
        """
        query = "SELECT * FROM calendar_events"
        conditions = []
        params = []
        
        if start_date:
            conditions.append("end_date >= ?")
            params.append(start_date)
            
        if end_date:
            conditions.append("start_date <= ?")
            params.append(end_date)
            
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
            
        if exam_id:
            conditions.append("exam_id = ?")
            params.append(exam_id)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY start_date ASC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
        
    def get_events_for_month(self, year, month):
        """
        Get all events for a specific month.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            list: List of event dictionaries
        """
        # First day of the month
        start_date = f"{year:04d}-{month:02d}-01"
        
        # Last day of the month (using the fact that the first day of next month minus 1 second is the last moment of current month)
        if month == 12:
            next_month_year = year + 1
            next_month = 1
        else:
            next_month_year = year
            next_month = month + 1
            
        end_date = f"{next_month_year:04d}-{next_month:02d}-01"
        
        return self.get_calendar_events(start_date, end_date)
        
    # Academic session methods
    def add_academic_session(self, name, start_date, end_date, description=None, color=None):
        """
        Add a new academic session (exam period).
        
        Args:
            name (str): Session name (e.g., 'Winter Session 2023')
            start_date (str): Start date (ISO format)
            end_date (str): End date (ISO format)
            description (str, optional): Session description
            color (str, optional): Session color (hex code)
            
        Returns:
            int: ID of the newly added session
        """
        now = datetime.now().isoformat()
        
        self.cursor.execute('''
        INSERT INTO academic_sessions (name, start_date, end_date, 
                                     description, color, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, start_date, end_date, description, color, now, now))
        
        self.conn.commit()
        return self.cursor.lastrowid
        
    def update_academic_session(self, session_id, name=None, start_date=None, 
                              end_date=None, description=None, color=None):
        """
        Update an existing academic session.
        
        Args:
            session_id (int): ID of the session to update
            [other args same as add_academic_session]
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get current values
        self.cursor.execute("SELECT * FROM academic_sessions WHERE id = ?", (session_id,))
        session = self.cursor.fetchone()
        
        if not session:
            return False
            
        # Use current values if new ones not provided
        name = name if name is not None else session['name']
        start_date = start_date if start_date is not None else session['start_date']
        end_date = end_date if end_date is not None else session['end_date']
        description = description if description is not None else session['description']
        color = color if color is not None else session['color']
        updated_at = datetime.now().isoformat()
        
        self.cursor.execute('''
        UPDATE academic_sessions
        SET name = ?, start_date = ?, end_date = ?, description = ?, color = ?, updated_at = ?
        WHERE id = ?
        ''', (name, start_date, end_date, description, color, updated_at, session_id))
        
        self.conn.commit()
        return True
        
    def delete_academic_session(self, session_id):
        """
        Delete an academic session.
        
        Args:
            session_id (int): ID of the session to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.cursor.execute("DELETE FROM academic_sessions WHERE id = ?", (session_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
        
    def get_academic_session(self, session_id):
        """
        Get a single academic session by ID.
        
        Args:
            session_id (int): ID of the session
            
        Returns:
            dict: Session data or None if not found
        """
        self.cursor.execute("SELECT * FROM academic_sessions WHERE id = ?", (session_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
        
    def get_academic_sessions(self, year=None):
        """
        Get all academic sessions, optionally filtered by year.
        
        Args:
            year (int, optional): Filter sessions by year
            
        Returns:
            list: List of session dictionaries
        """
        if year:
            year_str = f"{year:04d}"
            start_filter = f"{year_str}-01-01"
            end_filter = f"{year+1:04d}-01-01"
            
            self.cursor.execute("""
            SELECT * FROM academic_sessions 
            WHERE (start_date >= ? AND start_date < ?) OR 
                  (end_date >= ? AND end_date < ?) OR
                  (start_date < ? AND end_date >= ?)
            ORDER BY start_date ASC
            """, (start_filter, end_filter, start_filter, end_filter, start_filter, start_filter))
        else:
            self.cursor.execute("SELECT * FROM academic_sessions ORDER BY start_date ASC")
            
        return [dict(row) for row in self.cursor.fetchall()]
        
    def get_current_academic_sessions(self):
        """
        Get all current academic sessions (where today falls between start_date and end_date).
        
        Returns:
            list: List of current session dictionaries
        """
        today = datetime.now().date().isoformat()
        
        self.cursor.execute("""
        SELECT * FROM academic_sessions 
        WHERE start_date <= ? AND end_date >= ?
        ORDER BY start_date ASC
        """, (today, today))
            
        return [dict(row) for row in self.cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
