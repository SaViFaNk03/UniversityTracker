import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0
    @EnvironmentObject var appSettings: AppSettings
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.colorScheme) var colorScheme
    
    var body: some View {
        ZStack {
            // Sfondo personalizzato che cambia in base al tema
            themeManager.colors.background
                .edgesIgnoringSafeArea(.all)
            
            TabView(selection: $selectedTab) {
                DashboardView()
                    .tabItem {
                        Label(NSLocalizedString("Dashboard", comment: "Dashboard tab"), systemImage: "chart.bar.fill")
                    }
                    .tag(0)
                
                ExamsListView()
                    .tabItem {
                        Label(NSLocalizedString("Exams", comment: "Exams tab"), systemImage: "list.bullet.clipboard")
                    }
                    .tag(1)
                
                CalendarView()
                    .tabItem {
                        Label(NSLocalizedString("Calendar", comment: "Calendar tab"), systemImage: "calendar")
                    }
                    .tag(2)
                
                AnalyticsView()
                    .tabItem {
                        Label(NSLocalizedString("Analytics", comment: "Analytics tab"), systemImage: "function")
                    }
                    .tag(3)
                
                SettingsView()
                    .tabItem {
                        Label(NSLocalizedString("Settings", comment: "Settings tab"), systemImage: "gear")
                    }
                    .tag(4)
            }
            .accentColor(themeManager.colors.primary)
        }
        // Animazione fluida quando cambia il tema
        .animation(.easeInOut(duration: 0.3), value: themeManager.isDarkMode)
        .preferredColorScheme(themeManager.isDarkMode ? .dark : .light)
        // Rileva i cambiamenti del tema di sistema
        .onChange(of: colorScheme) { newColorScheme in
            // Aggiorna ThemeManager con il nuovo stato del tema di sistema
            themeManager.updateWithSystemTheme(isDark: newColorScheme == .dark)
        }
        .onAppear {
            // Al primo avvio, sincronizza con il tema di sistema
            themeManager.updateWithSystemTheme(isDark: colorScheme == .dark)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        let appSettings = AppSettings()
        let themeManager = ThemeManager()
        
        appSettings.themeManager = themeManager
        
        return Group {
            // Anteprima modalità chiara
            ContentView()
                .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
                .environmentObject(appSettings)
                .environmentObject(themeManager)
                .previewDisplayName("Light Mode")
            
            // Anteprima modalità scura
            ContentView()
                .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
                .environmentObject(appSettings)
                .environmentObject({
                    let darkThemeManager = ThemeManager()
                    darkThemeManager.isDarkMode = true
                    return darkThemeManager
                }())
                .previewDisplayName("Dark Mode")
        }
    }
}
