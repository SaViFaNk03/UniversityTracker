import Foundation
import SwiftUI
import Combine

class AppSettings: ObservableObject {
    private let persistenceController = PersistenceController.shared
    
    @Published var degreeName: String {
        didSet {
            persistenceController.updateSetting(key: "degree_name", value: degreeName)
        }
    }
    
    @Published var totalCredits: Int {
        didSet {
            persistenceController.updateSetting(key: "total_credits", value: String(totalCredits))
        }
    }
    
    @Published var maxGrade: Int {
        didSet {
            persistenceController.updateSetting(key: "max_grade", value: String(maxGrade))
        }
    }
    
    @Published var passThreshold: Int {
        didSet {
            persistenceController.updateSetting(key: "pass_threshold", value: String(passThreshold))
        }
    }
    
    @Published var targetAverage: Int {
        didSet {
            persistenceController.updateSetting(key: "target_average", value: String(targetAverage))
        }
    }
    
    @Published var isDarkMode: Bool = false
    @Published var selectedLanguage: String = "it"
    
    init() {
        // Load settings from persistence
        self.degreeName = persistenceController.getSetting(key: "degree_name", defaultValue: "Computer Science")
        self.totalCredits = Int(persistenceController.getSetting(key: "total_credits", defaultValue: "180")) ?? 180
        self.maxGrade = Int(persistenceController.getSetting(key: "max_grade", defaultValue: "30")) ?? 30
        self.passThreshold = Int(persistenceController.getSetting(key: "pass_threshold", defaultValue: "18")) ?? 18
        self.targetAverage = Int(persistenceController.getSetting(key: "target_average", defaultValue: "100")) ?? 100
        
        // Check system color scheme
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
            let userInterfaceStyle = windowScene.windows.first?.traitCollection.userInterfaceStyle ?? .light
            isDarkMode = userInterfaceStyle == .dark
        }
    }
    
    func resetSettings() {
        degreeName = "Computer Science"
        totalCredits = 180
        maxGrade = 30
        passThreshold = 18
        targetAverage = 100
    }
}
