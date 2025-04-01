class AcademicCalculator:
    """Performs academic calculations for university career metrics."""
    
    @staticmethod
    def calculate_simple_average(exams):
        """
        Calculate simple average (not weighted by credits).
        
        Args:
            exams (list): List of exam dictionaries with grades
            
        Returns:
            float: Simple average or 0 if no passed exams
        """
        passed_exams = [exam for exam in exams if exam['status'] == 'passed' and exam['grade'] is not None]
        
        if not passed_exams:
            return 0
            
        total_grade = sum(exam['grade'] for exam in passed_exams)
        return total_grade / len(passed_exams)
    
    @staticmethod
    def calculate_weighted_average(exams):
        """
        Calculate weighted average based on exam credits.
        
        Args:
            exams (list): List of exam dictionaries with grades and credits
            
        Returns:
            float: Weighted average or 0 if no passed exams
        """
        passed_exams = [exam for exam in exams if exam['status'] == 'passed' and exam['grade'] is not None]
        
        if not passed_exams:
            return 0
            
        weighted_sum = sum(exam['grade'] * exam['credits'] for exam in passed_exams)
        total_credits = sum(exam['credits'] for exam in passed_exams)
        
        return weighted_sum / total_credits if total_credits > 0 else 0
    
    @staticmethod
    def convert_to_110_scale(average, max_grade=30):
        """
        Convert average to 110 scale (Italian university system).
        
        Args:
            average (float): Current average (typically on a 30-point scale)
            max_grade (int): Maximum grade in the original scale
            
        Returns:
            float: Average converted to 110 scale
        """
        return (average / max_grade) * 110
    
    @staticmethod
    def calculate_total_credits(exams):
        """
        Calculate total credits earned from passed exams.
        
        Args:
            exams (list): List of exam dictionaries
            
        Returns:
            int: Total credits earned
        """
        passed_exams = [exam for exam in exams if exam['status'] == 'passed']
        return sum(exam['credits'] for exam in passed_exams)
    
    @staticmethod
    def calculate_remaining_credits(exams, total_required):
        """
        Calculate remaining credits needed for graduation.
        
        Args:
            exams (list): List of exam dictionaries
            total_required (int): Total credits required for graduation
            
        Returns:
            int: Remaining credits needed
        """
        earned_credits = AcademicCalculator.calculate_total_credits(exams)
        remaining = total_required - earned_credits
        return max(0, remaining)
    
    @staticmethod
    def calculate_required_grades(exams, planned_exams, target_average, max_grade=30, fixed_grades=None):
        """
        Calculate required grades for planned exams to reach target average,
        with higher grades assigned to easier exams (those with fewer credits)
        and lower grades to harder exams (those with more credits).
        
        Args:
            exams (list): List of all exam dictionaries
            planned_exams (list): List of planned exam dictionaries
            target_average (float): Target weighted average
            max_grade (int): Maximum possible grade
            fixed_grades (dict, optional): Dictionary with exam IDs as keys and manually set grades as values
            
        Returns:
            dict: Dictionary with planned exam IDs as keys and required grades as values
        """
        # If no fixed grades provided, initialize empty dict
        if fixed_grades is None:
            fixed_grades = {}
            
        # Get passed exams
        passed_exams = [exam for exam in exams if exam['status'] == 'passed' and exam['grade'] is not None]
        
        if not planned_exams:
            return {}
            
        # Calculate current weighted sum and credits
        current_weighted_sum = sum(exam['grade'] * exam['credits'] for exam in passed_exams)
        current_credits = sum(exam['credits'] for exam in passed_exams)
        
        # Separate fixed and adjustable exams
        fixed_exams = []
        adjustable_exams = []
        
        for exam in planned_exams:
            if exam['id'] in fixed_grades:
                fixed_exams.append(exam)
            else:
                adjustable_exams.append(exam)
                
        # If all exams are fixed, no calculation needed
        if not adjustable_exams:
            return fixed_grades
                
        # Calculate weighted sum and credits from fixed exams
        fixed_weighted_sum = sum(fixed_grades[exam['id']] * exam['credits'] for exam in fixed_exams)
        fixed_credits = sum(exam['credits'] for exam in fixed_exams)
        
        # Calculate adjustable credits
        adjustable_credits = sum(exam['credits'] for exam in adjustable_exams)
        
        # Calculate total credits including all planned exams
        total_credits = current_credits + fixed_credits + adjustable_credits
        
        # Calculate required weighted sum to achieve target average
        required_weighted_sum = target_average * total_credits
        
        # Calculate remaining weighted sum needed for adjustable exams
        remaining_weighted_sum = required_weighted_sum - current_weighted_sum - fixed_weighted_sum
        
        # Check if target is already achieved even without adjustable exams
        if remaining_weighted_sum <= 0:
            return {**fixed_grades, **{exam['id']: 0 for exam in adjustable_exams}}
            
        # Check if target is achievable with maximum grades for adjustable exams
        if remaining_weighted_sum > max_grade * adjustable_credits:
            # Target not achievable even with maximum grades
            return {**fixed_grades, **{exam['id']: max_grade for exam in adjustable_exams}}
        
        # If no adjustable exams, no further calculation needed
        if not adjustable_exams:
            return fixed_grades
        
        # New approach: distribute grades inversely proportional to credits
        # Exams with more credits (harder) get lower grades
        # Exams with fewer credits (easier) get higher grades
        
        # Step 1: Calculate difficulty factor for each exam based on credits
        if len(adjustable_exams) == 1:
            # If only one adjustable exam, simply calculate the required grade
            required_grade = remaining_weighted_sum / adjustable_exams[0]['credits']
            required_grade = min(max_grade, max(18, required_grade))
            return {**fixed_grades, **{adjustable_exams[0]['id']: required_grade}}
            
        max_credits = max(exam['credits'] for exam in adjustable_exams)
        min_credits = min(exam['credits'] for exam in adjustable_exams)
        
        # If all adjustable exams have the same number of credits, use equal distribution
        if max_credits == min_credits:
            average_grade_needed = remaining_weighted_sum / adjustable_credits
            average_grade_needed = min(max_grade, max(18, average_grade_needed))
            return {**fixed_grades, **{exam['id']: average_grade_needed for exam in adjustable_exams}}
        
        # Step 2: Create difficulty scale (inverse of credits)
        # Higher value = easier exam = higher grade
        difficulty_factors = {}
        difficulty_sum = 0
        
        for exam in adjustable_exams:
            # Normalize credits to a scale of 0-1 (inverted so higher credits = lower value)
            normalized_difficulty = (max_credits - exam['credits']) / (max_credits - min_credits)
            # Add a base factor to ensure even hard exams get reasonable grades
            difficulty_factor = 0.5 + (0.5 * normalized_difficulty)
            difficulty_factors[exam['id']] = difficulty_factor
            difficulty_sum += difficulty_factor * exam['credits']
        
        # Step 3: Calculate a base grade that, when adjusted by difficulty factors,
        # will achieve the target weighted sum
        base_grade = remaining_weighted_sum / difficulty_sum
        
        # Step 4: Calculate required grade for each adjustable exam
        result = dict(fixed_grades)  # Start with fixed grades
        for exam in adjustable_exams:
            # Apply difficulty factor to base grade
            grade = base_grade * difficulty_factors[exam['id']]
            # Ensure grade is within valid range
            grade = min(max_grade, max(18, grade))  # Min grade usually 18 in Italian system
            result[exam['id']] = grade
            
        return result
        
    @staticmethod
    def recalculate_with_fixed_grade(exams, planned_exams, target_average, exam_id, fixed_grade, max_grade=30, current_required_grades=None):
        """
        Recalculate required grades when one grade is manually fixed by the user.
        
        Args:
            exams (list): List of all exam dictionaries
            planned_exams (list): List of planned exam dictionaries
            target_average (float): Target weighted average
            exam_id (int): ID of the exam with the manually set grade
            fixed_grade (float): Manually set grade value
            max_grade (int): Maximum possible grade
            current_required_grades (dict, optional): Current required grades
            
        Returns:
            dict: Updated dictionary with exam IDs as keys and required grades as values
        """
        # Create fixed grades dictionary with the manually specified grade
        fixed_grades = {exam_id: fixed_grade}
        
        # Add any existing fixed grades, except for the one being modified
        if current_required_grades:
            for id, grade in current_required_grades.items():
                if id != exam_id and isinstance(grade, tuple):
                    # This is a fixed grade (set by user)
                    fixed_grades[id] = grade[0]
        
        # Calculate new required grades with the fixed grade
        new_grades = AcademicCalculator.calculate_required_grades(
            exams, planned_exams, target_average, max_grade, fixed_grades)
            
        # Mark the manually set grade as fixed (tuple with grade and True flag)
        result = dict(new_grades)
        result[exam_id] = (fixed_grade, True)
        
        return result
    
    @staticmethod
    def calculate_final_average_with_custom_grades(passed_exams, planned_exams, custom_grades, max_grade=30):
        """
        Calculate the final average when all planned exams have custom grades.
        
        Args:
            passed_exams (list): List of passed exam dictionaries
            planned_exams (list): List of planned exam dictionaries
            custom_grades (dict): Dictionary with exam IDs as keys and custom grades as values
            max_grade (int): Maximum possible grade
            
        Returns:
            tuple: (final_average, final_average_110) - the final average in original and 110 scale
        """
        # Calculate weighted sum and credits for passed exams
        current_weighted_sum = sum(exam['grade'] * exam['credits'] for exam in passed_exams)
        current_credits = sum(exam['credits'] for exam in passed_exams)
        
        # Calculate weighted sum and credits for planned exams with custom grades
        planned_weighted_sum = 0
        planned_credits = 0
        
        for exam in planned_exams:
            if exam['id'] in custom_grades:
                grade = custom_grades[exam['id']]
                planned_weighted_sum += grade * exam['credits']
                planned_credits += exam['credits']
        
        # Calculate final average
        total_weighted_sum = current_weighted_sum + planned_weighted_sum
        total_credits = current_credits + planned_credits
        
        if total_credits > 0:
            final_average = total_weighted_sum / total_credits
            final_average_110 = (final_average / max_grade) * 110
        else:
            final_average = 0
            final_average_110 = 0
            
        return (final_average, final_average_110)
        
    @staticmethod
    def calculate_progress_percentage(earned_credits, total_required):
        """
        Calculate percentage of degree completion.
        
        Args:
            earned_credits (int): Credits earned so far
            total_required (int): Total credits required for graduation
            
        Returns:
            float: Percentage of completion (0-100)
        """
        if total_required <= 0:
            return 0
            
        percentage = (earned_credits / total_required) * 100
        return min(100, max(0, percentage))  # Ensure between 0 and 100
        
    @staticmethod
    def calculate_completion_prediction(passed_exams, planned_exams, total_credits_required):
        """
        Predict when the degree will be completed based on the current study pace.
        
        Args:
            passed_exams (list): List of passed exam dictionaries with dates
            planned_exams (list): List of planned exam dictionaries
            total_credits_required (int): Total credits required for graduation
            
        Returns:
            dict: Dictionary with prediction results including:
                - 'estimated_completion_date': Predicted completion date
                - 'months_remaining': Estimated months remaining
                - 'pace_per_month': Average credits earned per month
                - 'exams_per_month': Average exams passed per month
                - 'credits_needed': Remaining credits needed
                - 'exams_needed': Remaining exams count
        """
        from datetime import datetime, timedelta
        
        # Get current date
        current_date = datetime.now()
        
        # Sort passed exams by date
        valid_passed_exams = [e for e in passed_exams if e.get('date')]
        
        # If no passed exams with valid dates, return None
        if not valid_passed_exams:
            return None
            
        # Sort exams by date
        valid_passed_exams.sort(key=lambda e: datetime.strptime(e['date'], '%Y-%m-%d'))
        
        # Calculate study duration in months
        start_date = datetime.strptime(valid_passed_exams[0]['date'], '%Y-%m-%d')
        study_duration_days = (current_date - start_date).days
        
        # Avoid division by zero
        if study_duration_days <= 0:
            study_duration_days = 1
            
        study_duration_months = study_duration_days / 30.44  # Average days per month
        
        # Calculate earned credits and pace
        earned_credits = sum(e['credits'] for e in passed_exams)
        needed_credits = total_credits_required - earned_credits
        
        # Calculate passed exams pace
        exams_count = len(passed_exams)
        
        # Avoid division by zero
        if study_duration_months <= 0:
            study_duration_months = 0.1
            
        exams_per_month = exams_count / study_duration_months
        credits_per_month = earned_credits / study_duration_months
        
        # Predict remaining time based on current pace
        if credits_per_month <= 0:
            credits_per_month = 0.1  # Avoid division by zero, assume minimal progress
            
        months_remaining = needed_credits / credits_per_month
        
        # Calculate estimated completion date
        completion_date = current_date + timedelta(days=int(months_remaining * 30.44))
        
        # Calculate remaining exams
        planned_exams_count = len(planned_exams)
        
        # Return prediction data
        return {
            'estimated_completion_date': completion_date.strftime('%Y-%m-%d'),
            'months_remaining': round(months_remaining, 1),
            'pace_per_month': round(credits_per_month, 1),
            'exams_per_month': round(exams_per_month, 1),
            'credits_needed': needed_credits,
            'exams_needed': planned_exams_count
        }
        
    @staticmethod
    def calculate_alternative_completion_scenarios(passed_exams, planned_exams, total_credits_required):
        """
        Calculate different degree completion scenarios with varied paces.
        
        Args:
            passed_exams (list): List of passed exam dictionaries
            planned_exams (list): List of planned exam dictionaries
            total_credits_required (int): Total credits required for graduation
            
        Returns:
            dict: Dictionary with alternative scenarios
        """
        from datetime import datetime, timedelta
        
        # Base prediction
        base_prediction = AcademicCalculator.calculate_completion_prediction(
            passed_exams, planned_exams, total_credits_required)
            
        if not base_prediction:
            return None
            
        # Current date
        current_date = datetime.now()
        
        # Calculate earned and needed credits
        earned_credits = sum(e['credits'] for e in passed_exams)
        needed_credits = total_credits_required - earned_credits
        
        # Calculate average credits per exam in planned exams
        if planned_exams:
            avg_credits_per_exam = sum(e['credits'] for e in planned_exams) / len(planned_exams)
        else:
            # Use average from passed exams if no planned exams
            avg_credits_per_exam = earned_credits / len(passed_exams) if passed_exams else 6  # Default to 6 credits
            
        # Calculate scenarios
        scenarios = {}
        
        # Scenario 1: 1 exam per month
        credits_per_month = avg_credits_per_exam * 1
        months_remaining = needed_credits / credits_per_month if credits_per_month > 0 else float('inf')
        completion_date = current_date + timedelta(days=int(months_remaining * 30.44))
        scenarios['slow_pace'] = {
            'exams_per_month': 1,
            'months_remaining': round(months_remaining, 1),
            'estimated_completion_date': completion_date.strftime('%Y-%m-%d')
        }
        
        # Scenario 2: 2 exams per month
        credits_per_month = avg_credits_per_exam * 2
        months_remaining = needed_credits / credits_per_month if credits_per_month > 0 else float('inf')
        completion_date = current_date + timedelta(days=int(months_remaining * 30.44))
        scenarios['medium_pace'] = {
            'exams_per_month': 2,
            'months_remaining': round(months_remaining, 1),
            'estimated_completion_date': completion_date.strftime('%Y-%m-%d')
        }
        
        # Scenario 3: 3 exams per month
        credits_per_month = avg_credits_per_exam * 3
        months_remaining = needed_credits / credits_per_month if credits_per_month > 0 else float('inf')
        completion_date = current_date + timedelta(days=int(months_remaining * 30.44))
        scenarios['fast_pace'] = {
            'exams_per_month': 3,
            'months_remaining': round(months_remaining, 1),
            'estimated_completion_date': completion_date.strftime('%Y-%m-%d')
        }
        
        return scenarios
