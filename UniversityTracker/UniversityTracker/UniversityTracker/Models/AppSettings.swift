import Foundation
import SwiftUI
import Combine

class AppSettings: ObservableObject {
    private let persistenceController = PersistenceController.shared
    var themeManager: ThemeManager!
    
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
    
    @Published var isDarkMode: Bool {
        didSet {
            // Sincronizza con il ThemeManager solo se non stiamo seguendo il tema di sistema
            if themeManager != nil && !themeManager.followSystemTheme {
                themeManager.isDarkMode = isDarkMode
                persistenceController.updateSetting(key: "is_dark_mode", value: String(isDarkMode))
            }
        }
    }
    
    @Published var selectedLanguage: String = "it" {
        didSet {
            persistenceController.updateSetting(key: "selected_language", value: selectedLanguage)
        }
    }
    
    init() {
        // Load settings from persistence
        self.degreeName = persistenceController.getSetting(key: "degree_name", defaultValue: "Computer Science")
        self.totalCredits = Int(persistenceController.getSetting(key: "total_credits", defaultValue: "180")) ?? 180
        self.maxGrade = Int(persistenceController.getSetting(key: "max_grade", defaultValue: "30")) ?? 30
        self.passThreshold = Int(persistenceController.getSetting(key: "pass_threshold", defaultValue: "18")) ?? 18
        self.targetAverage = Int(persistenceController.getSetting(key: "target_average", defaultValue: "100")) ?? 100
        
        // Leggi l'impostazione precedente del tema
        let savedIsDarkMode = persistenceController.getSetting(key: "is_dark_mode", defaultValue: "")
        
        // Se non c'è un'impostazione salvata, usa l'impostazione di sistema
        if savedIsDarkMode.isEmpty {
            if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
                let userInterfaceStyle = windowScene.windows.first?.traitCollection.userInterfaceStyle ?? .light
                isDarkMode = userInterfaceStyle == .dark
            } else {
                isDarkMode = false
            }
        } else {
            isDarkMode = savedIsDarkMode == "true"
        }
        
        // Inizializza il ThemeManager
        self.themeManager = ThemeManager()
        
        // Verifica se in precedenza è stato impostato di seguire il tema di sistema
        let followSystemTheme = UserDefaults.standard.bool(forKey: "followSystemTheme")
        
        if followSystemTheme {
            // In questo caso, il valore isDarkMode di ThemeManager verrà impostato 
            // automaticamente in base al tema di sistema tramite l'environment colorScheme
            self.themeManager.followSystemTheme = true
            
            // Anche se isDarkMode di AppSettings è impostato, non verrà usato se si segue il tema di sistema
        } else {
            // Se non seguiamo il tema di sistema, impostiamo manualmente isDarkMode di ThemeManager
            self.themeManager.followSystemTheme = false
            self.themeManager.isDarkMode = isDarkMode
        }
        
        // Carica la lingua selezionata
        self.selectedLanguage = persistenceController.getSetting(key: "selected_language", defaultValue: "it")
    }
    
    func resetSettings() {
        degreeName = "Computer Science"
        totalCredits = 180
        maxGrade = 30
        passThreshold = 18
        targetAverage = 100
    }
}
