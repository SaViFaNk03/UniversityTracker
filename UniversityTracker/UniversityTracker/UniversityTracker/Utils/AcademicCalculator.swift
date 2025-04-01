import Foundation

struct AcademicCalculator {
    
    /// Calculate the total credits earned from passed exams
    func calculateTotalCredits(exams: [Exam]) -> Int {
        return exams
            .filter { $0.status == .passed }
            .reduce(0) { $0 + $1.credits }
    }
    
    /// Calculate the simple average of grades (not weighted by credits)
    func calculateSimpleAverage(exams: [Exam]) -> Double {
        let passedExams = exams.filter { $0.status == .passed && $0.grade != nil }
        
        if passedExams.isEmpty {
            return 0.0
        }
        
        let sum = passedExams.reduce(0.0) { $0 + ($1.grade ?? 0) }
        return sum / Double(passedExams.count)
    }
    
    /// Calculate the weighted average of grades (weighted by credits)
    func calculateWeightedAverage(exams: [Exam]) -> Double {
        let passedExams = exams.filter { $0.status == .passed && $0.grade != nil }
        
        if passedExams.isEmpty {
            return 0.0
        }
        
        let weightedSum = passedExams.reduce(0.0) { $0 + ($1.grade ?? 0) * Double($1.credits) }
        let totalCredits = passedExams.reduce(0) { $0 + $1.credits }
        
        return weightedSum / Double(totalCredits)
    }
    
    /// Convert a grade from one scale to 110 scale (Italian degree final grade)
    func convertTo110Scale(grade: Double, maxGrade: Int) -> Double {
        return (grade / Double(maxGrade)) * 110.0
    }
    
    /// Calculate progress percentage toward degree completion
    func calculateProgressPercentage(earnedCredits: Int, totalRequiredCredits: Int) -> Double {
        guard totalRequiredCredits > 0 else { return 0.0 }
        return (Double(earnedCredits) / Double(totalRequiredCredits)) * 100.0
    }
    
    /// Calculate the required grades for remaining exams to reach target average
    func calculateRequiredGrades(
        allExams: [Exam],
        plannedExams: [Exam],
        targetAverage: Double,
        maxGrade: Int,
        fixedGrades: [UUID: Double] = [:]
    ) -> [UUID: Double] {
        
        guard !plannedExams.isEmpty else { return [:] }
        
        // Get passed exams with grades
        let passedExams = allExams.filter { $0.status == .passed && $0.grade != nil }
        
        // Calculate current weighted sum
        let currentWeightedSum = passedExams.reduce(0.0) { $0 + ($1.grade ?? 0) * Double($1.credits) }
        let currentCredits = passedExams.reduce(0) { $0 + $1.credits }
        
        // Calculate total credits including planned
        let plannedCredits = plannedExams.reduce(0) { $0 + $1.credits }
        let totalCredits = currentCredits + plannedCredits
        
        // Calculate required weighted sum to reach target
        let requiredWeightedSum = targetAverage * Double(totalCredits)
        let remainingWeightedSum = requiredWeightedSum - currentWeightedSum
        
        // Calculate target grades for planned exams
        var requiredGrades: [UUID: Double] = [:]
        
        // First, account for fixed grades
        var remainingPlannedExams = plannedExams
        var adjustedRemainingSum = remainingWeightedSum
        var adjustedRemainingCredits = plannedCredits
        
        for (examId, grade) in fixedGrades {
            if let index = remainingPlannedExams.firstIndex(where: { $0.id == examId }) {
                let exam = remainingPlannedExams[index]
                requiredGrades[examId] = grade
                adjustedRemainingSum -= grade * Double(exam.credits)
                adjustedRemainingCredits -= exam.credits
                remainingPlannedExams.remove(at: index)
            }
        }
        
        // Calculate equal grade distribution for remaining exams
        if adjustedRemainingCredits > 0 {
            let averageGrade = adjustedRemainingSum / Double(adjustedRemainingCredits)
            
            // Constrain to valid grades
            let constrainedGrade = min(Double(maxGrade), max(18.0, averageGrade))
            
            // Assign grades to remaining exams
            for exam in remainingPlannedExams {
                requiredGrades[exam.id] = constrainedGrade
            }
        }
        
        return requiredGrades
    }
}
