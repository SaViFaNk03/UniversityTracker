import Foundation

enum LocalizableString {
    case dashboard
    case exams
    case calendar
    case analytics
    case settings
    
    // Dashboard
    case overview
    case creditsEarned
    case average
    case weightedAverage
    case examsPassed
    case progressTowardDegree
    case completed
    case noExamsToDisplay
    case noGradesToDisplay
    
    // Exams
    case examManagement
    case filter
    case allExams
    case passed
    case failed
    case planned
    case addExam
    case editExam
    case deleteExam
    case schedule
    case id
    case examName
    case credits
    case grade
    case status
    case date
    case actions
    case save
    case cancel
    case notes
    case deleteConfirmation
    case deleteWarning
    
    // Calendar
    case academicCalendar
    case today
    case addEvent
    case addSession
    case eventsForDay
    case time
    case title
    case type
    case location
    case allDay
    case startDate
    case endDate
    case color
    case personal
    case exam
    case study
    case meeting
    case other
    
    // Analytics
    case targetCalculation
    case targetParameters
    case targetAverage
    case calculate
    case resetAllAutoGrades
    case autoMode
    case manualMode
    case mode
    case requiredGradesForTarget
    case doubleClickToEdit
    case adjustGradesManually
    
    // Settings
    case degreeSettings
    case degreeName
    case totalCreditsRequired
    case gradingSystem
    case maximumGrade
    case passingThreshold
    case targetSettings
    case dataManagement
    case exportData
    case importData
    case resetAllData
    case saveSettings
    case invalidSettings
    case settingsSaved
    case exportSuccessful
    case exportFailed
    case importSuccessful
    case importFailed
    case confirmImport
    case confirmReset
    case finalConfirmation
    case resetComplete
    case resetFailed
    
    var localized: String {
        return NSLocalizedString(String(describing: self), comment: "")
    }
}
