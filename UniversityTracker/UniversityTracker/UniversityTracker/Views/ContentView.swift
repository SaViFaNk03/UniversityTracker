import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0
    
    var body: some View {
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
        .accentColor(.blue)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
            .environmentObject(AppSettings())
    }
}
