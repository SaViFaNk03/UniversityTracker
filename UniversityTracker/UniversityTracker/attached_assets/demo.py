import sys
import os
import json
from datetime import datetime

# This is a simple console-based demonstration of the University Tracker
# Since PyQt5 is challenging to run in the Replit environment

class UniversityTrackerDemo:
    """A simple console-based demonstration of the University Tracker app."""
    
    def __init__(self):
        """Initialize the demo application."""
        self.exams = []
        self.load_demo_data()
        
    def load_demo_data(self):
        """Load some demo exam data."""
        self.exams = [
            {
                "id": 1,
                "name": "Mathematics",
                "credits": 6,
                "grade": 27,
                "status": "passed",
                "date": "2024-01-15"
            },
            {
                "id": 2,
                "name": "Computer Science",
                "credits": 9,
                "grade": 30,
                "status": "passed",
                "date": "2024-02-10"
            },
            {
                "id": 3,
                "name": "Physics",
                "credits": 6,
                "grade": 24,
                "status": "passed",
                "date": "2024-02-28"
            },
            {
                "id": 4,
                "name": "Electronics",
                "credits": 9,
                "grade": None,
                "status": "planned",
                "date": "2024-05-20"
            },
            {
                "id": 5,
                "name": "Software Engineering",
                "credits": 12,
                "grade": None,
                "status": "planned",
                "date": "2024-06-15"
            }
        ]
        
    def run(self):
        """Run the demo application."""
        while True:
            self.print_menu()
            choice = input("Enter your choice (1-6): ")
            
            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.show_exams()
            elif choice == "3":
                self.show_calendar()
            elif choice == "4":
                self.show_analytics()
            elif choice == "5":
                self.show_settings()
            elif choice == "6":
                print("\nThank you for using University Tracker Demo! Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
            
    def print_menu(self):
        """Print the main menu."""
        os.system('clear')
        print("=" * 60)
        print("            UNIVERSITY TRACKER DEMO               ")
        print("=" * 60)
        print("\nMain Menu:")
        print("1. Dashboard")
        print("2. Exams Management")
        print("3. Calendar")
        print("4. Analytics")
        print("5. Settings")
        print("6. Exit")
        print("\n" + "-" * 60)
        
    def show_dashboard(self):
        """Show dashboard with overview statistics."""
        os.system('clear')
        print("=" * 60)
        print("                 DASHBOARD                   ")
        print("=" * 60)
        
        # Calculate statistics
        passed_exams = [e for e in self.exams if e["status"] == "passed"]
        total_credits = sum(e["credits"] for e in passed_exams)
        
        if passed_exams:
            simple_avg = sum(e["grade"] for e in passed_exams) / len(passed_exams)
            weighted_sum = sum(e["grade"] * e["credits"] for e in passed_exams)
            weighted_avg = weighted_sum / total_credits
            # Convert to 110 scale (Italian university system)
            avg_110 = (weighted_avg / 30) * 110
        else:
            simple_avg = 0
            weighted_avg = 0
            avg_110 = 0
        
        # Progress calculation
        total_required = 180  # Example: typical bachelor's degree
        progress_percent = (total_credits / total_required) * 100
        
        print("\nStatistics:")
        print(f"✓ Credits Earned: {total_credits}/{total_required}")
        print(f"✓ Exams Passed: {len(passed_exams)}")
        print(f"✓ Simple Average: {simple_avg:.2f}/30")
        print(f"✓ Weighted Average: {weighted_avg:.2f}/30")
        print(f"✓ Degree Average (110 scale): {avg_110:.2f}/110")
        print(f"✓ Progress: {progress_percent:.1f}% completed")
        
        print("\nRecent Exams:")
        sorted_exams = sorted(passed_exams, key=lambda e: e["date"], reverse=True)
        for i, exam in enumerate(sorted_exams[:3]):
            print(f"{i+1}. {exam['name']} - Grade: {exam['grade']}/30 - Date: {exam['date']}")
            
    def show_exams(self):
        """Show exams management interface."""
        os.system('clear')
        print("=" * 60)
        print("              EXAMS MANAGEMENT                ")
        print("=" * 60)
        
        print("\nAll Exams:")
        print("-" * 60)
        print(f"{'ID':3} | {'Name':<20} | {'Credits':7} | {'Grade':5} | {'Status':<8} | {'Date':<10}")
        print("-" * 60)
        
        for exam in self.exams:
            grade_display = str(exam["grade"]) if exam["grade"] else "-"
            print(f"{exam['id']:3} | {exam['name']:<20} | {exam['credits']:7} | {grade_display:5} | {exam['status']:<8} | {exam['date']:<10}")
            
        print("\nExam Management Options:")
        print("- In the full app, you can add, edit, and delete exams")
        print("- Exams can be filtered by status (passed, failed, planned)")
        print("- You can schedule exams and track your progress")
        
    def show_calendar(self):
        """Show calendar view."""
        os.system('clear')
        print("=" * 60)
        print("               CALENDAR VIEW                 ")
        print("=" * 60)
        
        # Get current month calendar
        current_month = datetime.now().month
        current_year = datetime.now().year
        month_name = datetime(current_year, current_month, 1).strftime("%B %Y")
        
        print(f"\nCalendar: {month_name}")
        print("-" * 60)
        print("Mon  Tue  Wed  Thu  Fri  Sat  Sun")
        
        # Demo calendar
        print("                 1    2    3    4")
        print(" 5    6    7    8    9   10   11")
        print("12   13   14   15   16   17   18")
        print("19   20*  21   22   23   24   25")
        print("26   27   28   29   30")
        
        print("\n* = Exam scheduled")
        
        print("\nUpcoming Exams:")
        for exam in self.exams:
            if exam["status"] == "planned":
                print(f"- {exam['name']} on {exam['date']} ({exam['credits']} credits)")
                
        print("\nCalendar Features:")
        print("- In the full app, you can view and manage your academic schedule")
        print("- Add exams, study sessions, and personal events")
        print("- View events by day, week, or month")
        print("- Color-coded events for easy visualization")
        
    def show_analytics(self):
        """Show analytics and projections."""
        os.system('clear')
        print("=" * 60)
        print("                ANALYTICS                    ")
        print("=" * 60)
        
        passed_exams = [e for e in self.exams if e["status"] == "passed"]
        planned_exams = [e for e in self.exams if e["status"] == "planned"]
        
        # Calculate current statistics
        total_credits = sum(e["credits"] for e in passed_exams)
        if passed_exams:
            weighted_sum = sum(e["grade"] * e["credits"] for e in passed_exams)
            current_avg = weighted_sum / total_credits
            current_avg_110 = (current_avg / 30) * 110
        else:
            current_avg = 0
            current_avg_110 = 0
            
        target_avg_110 = 105  # Example target
        
        print("\nCurrent Performance:")
        print(f"Current Weighted Average: {current_avg:.2f}/30 ({current_avg_110:.2f}/110)")
        print(f"Target Average: {target_avg_110}/110")
        
        print("\nRequired Grades for Planned Exams:")
        print("-" * 60)
        print(f"{'Exam':<20} | {'Credits':7} | {'Required Grade':14}")
        print("-" * 60)
        
        # Simple algorithm to suggest required grades
        planned_credits = sum(e["credits"] for e in planned_exams)
        if planned_exams and passed_exams:
            target_avg_30 = (target_avg_110 / 110) * 30
            required_sum = target_avg_30 * (total_credits + planned_credits) - weighted_sum
            
            for exam in planned_exams:
                # Assign slightly higher grades to exams with fewer credits
                credits_factor = 1 - (exam["credits"] / 15)  # Normalize: higher for lower credits
                required_grade = min(30, 28 + (credits_factor * 2))
                print(f"{exam['name']:<20} | {exam['credits']:7} | {required_grade:.1f}/30")
        else:
            for exam in planned_exams:
                print(f"{exam['name']:<20} | {exam['credits']:7} | {'N/A':14}")
        
        print("\nAnalytics Features:")
        print("- The full app calculates exact required grades to reach your target")
        print("- View grade trends and performance over time")
        print("- Track credit accumulation progress")
        print("- Visualize grade distribution")
        
    def show_settings(self):
        """Show settings interface."""
        os.system('clear')
        print("=" * 60)
        print("                 SETTINGS                    ")
        print("=" * 60)
        
        print("\nDegree Settings:")
        print("Degree Name: Computer Science Engineering")
        print("Total Credits Required: 180")
        
        print("\nGrading System:")
        print("Maximum Grade: 30")
        print("Passing Threshold: 18")
        
        print("\nTarget Settings:")
        print("Target Average (110 scale): 105")
        
        print("\nAppearance:")
        print("Dark Mode: Enabled")
        
        print("\nData Management:")
        print("- Export Data")
        print("- Import Data")
        print("- Reset All Data")
        
        print("\nSettings Features:")
        print("- The full app allows you to customize all these parameters")
        print("- Settings are saved between sessions")
        print("- You can export and import data for backup and transfer")
        

if __name__ == "__main__":
    print("Welcome to University Tracker Demo!")
    print("This is a simplified console-based demonstration of the iOS University Tracker application.")
    print("The full application includes all features with a complete graphical interface.")
    print("\nPress Enter to continue...")
    input()
    
    app = UniversityTrackerDemo()
    app.run()