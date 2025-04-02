import SwiftUI

@main
struct UniversityTrackerApp: App {
    let persistenceController = PersistenceController.shared
    @StateObject private var appSettings = AppSettings()
    @StateObject private var themeManager = ThemeManager()
    
    init() {
        // Assicuriamoci che AppSettings e ThemeManager siano sincronizzati
        let settings = AppSettings()
        settings.themeManager = themeManager
        _appSettings = StateObject(wrappedValue: settings)
        
        // Configura il tema globale dell'app
        _themeManager = StateObject(wrappedValue: themeManager)
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
                .environmentObject(appSettings)
                .environmentObject(themeManager)
                // Il preferredColorScheme è gestito in ContentView per le animazioni
        }
    }
}
