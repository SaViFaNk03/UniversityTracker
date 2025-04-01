from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QFrame, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from calculations import AcademicCalculator

class PieChartWidget(FigureCanvas):
    """Widget for displaying a pie chart of exam status."""
    
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(PieChartWidget, self).__init__(self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def update_chart(self, passed_count, failed_count, planned_count):
        """Update the pie chart with new data."""
        self.axes.clear()
        
        # Data
        labels = ['Superati', 'Non Superati', 'Pianificati']
        sizes = [passed_count, failed_count, planned_count]
        colors = ['#4CAF50', '#F44336', '#2196F3']
        explode = (0.1, 0, 0)  # explode the 1st slice (Superati)
        
        # Only include categories with non-zero values
        non_zero_labels = []
        non_zero_sizes = []
        non_zero_colors = []
        non_zero_explode = []
        
        for i, size in enumerate(sizes):
            if size > 0:
                non_zero_labels.append(labels[i])
                non_zero_sizes.append(size)
                non_zero_colors.append(colors[i])
                non_zero_explode.append(explode[i] if i < len(explode) else 0)
        
        if sum(non_zero_sizes) > 0:
            self.axes.pie(non_zero_sizes, explode=non_zero_explode, labels=non_zero_labels, 
                         colors=non_zero_colors, autopct='%1.1f%%', shadow=True, startangle=90)
        else:
            self.axes.text(0.5, 0.5, "Nessun esame da visualizzare", 
                          horizontalalignment='center', verticalalignment='center')
            
        self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        self.fig.tight_layout()
        self.draw()

class BarChartWidget(FigureCanvas):
    """Widget for displaying a bar chart of grades distribution."""
    
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(BarChartWidget, self).__init__(self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def update_chart(self, exams, max_grade=30):
        """Update the bar chart with new grade distribution."""
        self.axes.clear()
        
        # Extract grades from passed exams
        grades = [exam['grade'] for exam in exams 
                 if exam['status'] == 'passed' and exam['grade'] is not None]
        
        if not grades:
            self.axes.text(0.5, 0.5, "Nessun voto da visualizzare", 
                          horizontalalignment='center', verticalalignment='center')
            self.draw()
            return
            
        # Create bins for grades (18-30 in Italian system)
        bins = list(range(18, max_grade + 2))
        
        # Create histogram
        self.axes.hist(grades, bins=bins, alpha=0.7, color='#2196F3', edgecolor='black')
        
        # Add labels and title
        self.axes.set_xlabel('Voti')
        self.axes.set_ylabel('Frequenza')
        self.axes.set_title('Distribuzione dei Voti')
        
        # Set x-ticks
        self.axes.set_xticks(list(range(18, max_grade + 1)))
        
        self.fig.tight_layout()
        self.draw()

class StatCard(QFrame):
    """A card widget displaying a statistic with title and value."""
    
    def __init__(self, title, value, parent=None):
        super(StatCard, self).__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set minimum height
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout()
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.title_label.setFont(font)
        
        # Value label
        self.value_label = QLabel(str(value))
        self.value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(16)
        self.value_label.setFont(value_font)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)
        
    def update_value(self, value):
        """Update the displayed value."""
        self.value_label.setText(str(value))


class DashboardWidget(QWidget):
    """Dashboard widget showing overview of academic progress."""
    
    def __init__(self, db_manager):
        super(DashboardWidget, self).__init__()
        self.db_manager = db_manager
        self.calculator = AcademicCalculator()
        
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the dashboard UI."""
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Panoramica")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Cards section
        cards_layout = QGridLayout()
        
        # Create stat cards
        self.credits_card = StatCard("CFU Conseguiti", "0/0")
        self.average_card = StatCard("Media (110)", "0.0")
        self.weighted_avg_card = StatCard("Media Ponderata (110)", "0.0")
        self.exams_passed_card = StatCard("Esami Superati", "0")
        
        # Add cards to grid
        cards_layout.addWidget(self.credits_card, 0, 0)
        cards_layout.addWidget(self.average_card, 0, 1)
        cards_layout.addWidget(self.weighted_avg_card, 1, 0)
        cards_layout.addWidget(self.exams_passed_card, 1, 1)
        
        # Add cards section to main layout
        cards_container = QWidget()
        cards_container.setLayout(cards_layout)
        main_layout.addWidget(cards_container)
        
        # Progress bar section
        progress_layout = QVBoxLayout()
        
        progress_label = QLabel("Progresso Verso la Laurea")
        progress_label.setAlignment(Qt.AlignCenter)
        progress_font = QFont()
        progress_font.setBold(True)
        progress_label.setFont(progress_font)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% completato")
        
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        progress_container = QWidget()
        progress_container.setLayout(progress_layout)
        main_layout.addWidget(progress_container)
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Pie chart for exam status distribution
        self.pie_chart = PieChartWidget(self, width=4, height=4)
        charts_layout.addWidget(self.pie_chart)
        
        # Bar chart for grade distribution
        self.bar_chart = BarChartWidget(self, width=4, height=4)
        charts_layout.addWidget(self.bar_chart)
        
        charts_container = QWidget()
        charts_container.setLayout(charts_layout)
        main_layout.addWidget(charts_container)
        
        self.setLayout(main_layout)
        
    @pyqtSlot()
    def refresh_data(self):
        """Refresh dashboard with latest data from the database."""
        # Get all exams
        all_exams = self.db_manager.get_all_exams()
        passed_exams = self.db_manager.get_passed_exams()
        failed_exams = self.db_manager.get_failed_exams()
        planned_exams = self.db_manager.get_planned_exams()
        
        # Get degree settings
        total_required_credits = int(self.db_manager.get_setting('total_credits', 180))
        max_grade = int(self.db_manager.get_setting('max_grade', 30))
        
        # Calculate statistics
        earned_credits = self.calculator.calculate_total_credits(all_exams)
        simple_avg = self.calculator.calculate_simple_average(all_exams)
        weighted_avg = self.calculator.calculate_weighted_average(all_exams)
        
        # Convert averages to 110 scale
        simple_avg_110 = self.calculator.convert_to_110_scale(simple_avg, max_grade)
        weighted_avg_110 = self.calculator.convert_to_110_scale(weighted_avg, max_grade)
        
        # Calculate progress
        progress_percentage = self.calculator.calculate_progress_percentage(
            earned_credits, total_required_credits)
        
        # Update UI elements
        self.credits_card.update_value(f"{earned_credits}/{total_required_credits}")
        self.average_card.update_value(f"{simple_avg_110:.2f}")
        self.weighted_avg_card.update_value(f"{weighted_avg_110:.2f}")
        self.exams_passed_card.update_value(str(len(passed_exams)))
        
        self.progress_bar.setValue(int(progress_percentage))
        
        # Update charts
        passed_count = len(passed_exams)
        failed_count = len(failed_exams)
        planned_count = len(planned_exams)
        
        self.pie_chart.update_chart(passed_count, failed_count, planned_count)
        self.bar_chart.update_chart(passed_exams, max_grade)
