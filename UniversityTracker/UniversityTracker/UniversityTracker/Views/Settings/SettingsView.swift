import SwiftUI
import UniformTypeIdentifiers

struct SettingsView: View {
    @EnvironmentObject private var appSettings: AppSettings
    @EnvironmentObject private var themeManager: ThemeManager
    @Environment(\.managedObjectContext) private var viewContext
    @State private var isImporting = false
    @State private var isExporting = false
    @State private var showingResetAlert = false
    @State private var showingConfirmResetAlert = false
    @State private var showingSuccessMessage = false
    @State private var successMessage = ""
    @State private var showingErrorMessage = false
    @State private var errorMessage = ""
    @State private var showThemeSettings = false
    
    @State private var degreeName: String
    @State private var totalCredits: Int
    @State private var maxGrade: Int
    @State private var passThreshold: Int
    @State private var targetAverage: Int
    @State private var isDarkMode: Bool
    
    // Initialize the state variables with the current app settings
    init() {
        let settings = AppSettings()
        _degreeName = State(initialValue: settings.degreeName)
        _totalCredits = State(initialValue: settings.totalCredits)
        _maxGrade = State(initialValue: settings.maxGrade)
        _passThreshold = State(initialValue: settings.passThreshold)
        _targetAverage = State(initialValue: settings.targetAverage)
        _isDarkMode = State(initialValue: settings.isDarkMode)
    }
    
    var body: some View {
        NavigationView {
            Form {
                // Degree settings section
                Section(header: Text(NSLocalizedString("Degree Settings", comment: "Section title"))
                    .foregroundColor(themeManager.colors.secondaryText)) {
                    TextField(NSLocalizedString("Degree Name", comment: "Field label"), text: $degreeName)
                        .foregroundColor(themeManager.colors.text)
                    
                    Stepper(value: $totalCredits, in: 1...500) {
                        HStack {
                            Text(NSLocalizedString("Total Credits Required", comment: "Field label"))
                                .foregroundColor(themeManager.colors.text)
                            Spacer()
                            Text("\(totalCredits)")
                                .foregroundColor(themeManager.colors.secondaryText)
                        }
                    }
                }
                .listRowBackground(themeManager.colors.secondaryBackground)
                
                // Grading system section
                Section(header: Text(NSLocalizedString("Grading System", comment: "Section title"))
                    .foregroundColor(themeManager.colors.secondaryText)) {
                    Stepper(value: $maxGrade, in: 1...100) {
                        HStack {
                            Text(NSLocalizedString("Maximum Grade", comment: "Field label"))
                                .foregroundColor(themeManager.colors.text)
                            Spacer()
                            Text("\(maxGrade)")
                                .foregroundColor(themeManager.colors.secondaryText)
                        }
                    }
                    
                    Stepper(value: $passThreshold, in: 1...$maxGrade.wrappedValue) {
                        HStack {
                            Text(NSLocalizedString("Passing Threshold", comment: "Field label"))
                                .foregroundColor(themeManager.colors.text)
                            Spacer()
                            Text("\(passThreshold)")
                                .foregroundColor(themeManager.colors.secondaryText)
                        }
                    }
                }
                .listRowBackground(themeManager.colors.secondaryBackground)
                
                // Target settings section
                Section(header: Text(NSLocalizedString("Target Settings", comment: "Section title"))
                    .foregroundColor(themeManager.colors.secondaryText)) {
                    Stepper(value: $targetAverage, in: 18...110) {
                        HStack {
                            Text(NSLocalizedString("Target Average (110 scale)", comment: "Field label"))
                                .foregroundColor(themeManager.colors.text)
                            Spacer()
                            Text("\(targetAverage)")
                                .foregroundColor(themeManager.colors.secondaryText)
                        }
                    }
                }
                .listRowBackground(themeManager.colors.secondaryBackground)
                
                // Appearance section
                Section(header: Text(NSLocalizedString("Appearance", comment: "Section title"))
                    .foregroundColor(themeManager.colors.secondaryText)) {
                    
                    NavigationLink(
                        destination: ThemeSettingsView()
                            .environmentObject(themeManager)
                            .navigationTitle(NSLocalizedString("Theme Settings", comment: "View title")),
                        isActive: $showThemeSettings
                    ) {
                        HStack {
                            Text(NSLocalizedString("Theme", comment: "Field label"))
                                .foregroundColor(themeManager.colors.text)
                            
                            Spacer()
                            
                            // Visualizzazione della modalità attuale
                            HStack(spacing: 6) {
                                if themeManager.followSystemTheme {
                                    Image(systemName: "iphone")
                                        .foregroundColor(themeManager.colors.primary)
                                        .imageScale(.small)
                                    
                                    Text(NSLocalizedString("Auto", comment: "Theme mode"))
                                        .foregroundColor(themeManager.colors.secondaryText)
                                } else {
                                    Image(systemName: themeManager.isDarkMode ? "moon.fill" : "sun.max.fill")
                                        .foregroundColor(themeManager.isDarkMode ? .yellow : .orange)
                                        .imageScale(.small)
                                    
                                    Text(themeManager.isDarkMode ? 
                                         NSLocalizedString("Dark", comment: "Theme mode") : 
                                         NSLocalizedString("Light", comment: "Theme mode"))
                                        .foregroundColor(themeManager.colors.secondaryText)
                                }
                            }
                        }
                    }
                    
                    // Toggle per seguire il tema di sistema
                    Toggle(NSLocalizedString("Use System Appearance", comment: "Field label"), 
                           isOn: $themeManager.followSystemTheme.animation(.easeInOut(duration: 0.3)))
                        .foregroundColor(themeManager.colors.text)
                        .toggleStyle(SwitchToggleStyle(tint: themeManager.colors.accent))
                        .onChange(of: themeManager.followSystemTheme) { newValue in
                            if newValue {
                                // Se attivata, imposta il valore a isDarkMode
                                isDarkMode = themeManager.isDarkMode
                            }
                        }
                    
                    // Toggle per dark mode (disabilitato se usiamo il tema di sistema)
                    Toggle(NSLocalizedString("Dark Mode", comment: "Field label"), 
                           isOn: $isDarkMode.animation(.easeInOut(duration: 0.3)))
                        .foregroundColor(themeManager.colors.text)
                        .toggleStyle(SwitchToggleStyle(tint: themeManager.colors.accent))
                        .disabled(themeManager.followSystemTheme)
                        .opacity(themeManager.followSystemTheme ? 0.6 : 1.0)
                }
                .listRowBackground(themeManager.colors.secondaryBackground)
                
                // Data management section
                Section(header: Text(NSLocalizedString("Data Management", comment: "Section title"))
                    .foregroundColor(themeManager.colors.secondaryText)) {
                    Button(action: { isExporting = true }) {
                        Label(
                            NSLocalizedString("Export Data", comment: "Button label"),
                            systemImage: "square.and.arrow.up"
                        )
                        .foregroundColor(themeManager.colors.text)
                    }
                    
                    Button(action: { isImporting = true }) {
                        Label(
                            NSLocalizedString("Import Data", comment: "Button label"),
                            systemImage: "square.and.arrow.down"
                        )
                        .foregroundColor(themeManager.colors.text)
                    }
                    
                    Button(action: { showingResetAlert = true }) {
                        Label(
                            NSLocalizedString("Reset All Data", comment: "Button label"),
                            systemImage: "trash"
                        )
                        .foregroundColor(.red)
                    }
                }
                .listRowBackground(themeManager.colors.secondaryBackground)
                
                // Save button section
                Section {
                    Button(action: saveSettings) {
                        Text(NSLocalizedString("Save Settings", comment: "Button label"))
                            .frame(maxWidth: .infinity, alignment: .center)
                            .foregroundColor(themeManager.colors.buttonText)
                            .padding(.vertical, 8)
                    }
                    .listRowBackground(themeManager.colors.buttonBackground)
                }
            }
            .navigationTitle(NSLocalizedString("Settings", comment: "View title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    ThemeSwitcherButton(compact: true)
                        .environmentObject(themeManager)
                }
            }
            // Import/Export sheet
            .fileImporter(
                isPresented: $isImporting,
                allowedContentTypes: [UTType.database],
                allowsMultipleSelection: false
            ) { result in
                handleImport(result: result)
            }
            .fileExporter(
                isPresented: $isExporting,
                document: DatabaseDocument(),
                contentType: UTType.database,
                defaultFilename: "university_tracker.db"
            ) { result in
                handleExport(result: result)
            }
            // Alerts
            .alert(isPresented: $showingResetAlert) {
                Alert(
                    title: Text(NSLocalizedString("Confirm Reset", comment: "Alert title")),
                    message: Text(NSLocalizedString("This will delete ALL your data including exams and settings. This action cannot be undone. Are you sure?", comment: "Alert message")),
                    primaryButton: .destructive(Text(NSLocalizedString("Yes", comment: "Button"))) {
                        showingConfirmResetAlert = true
                    },
                    secondaryButton: .cancel()
                )
            }
            .alert(isPresented: $showingConfirmResetAlert) {
                Alert(
                    title: Text(NSLocalizedString("Final Confirmation", comment: "Alert title")),
                    message: Text(NSLocalizedString("ALL DATA WILL BE PERMANENTLY DELETED. Proceed?", comment: "Alert message")),
                    primaryButton: .destructive(Text(NSLocalizedString("Yes", comment: "Button"))) {
                        resetData()
                    },
                    secondaryButton: .cancel()
                )
            }
            .alert(NSLocalizedString("Success", comment: "Alert title"), isPresented: $showingSuccessMessage) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(successMessage)
            }
            .alert(NSLocalizedString("Error", comment: "Alert title"), isPresented: $showingErrorMessage) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(errorMessage)
            }
            .onAppear {
                // Load current values when view appears
                loadCurrentSettings()
            }
            .background(themeManager.colors.background)
            .onChange(of: isDarkMode) { newValue in
                withAnimation(.easeInOut(duration: 0.3)) {
                    themeManager.isDarkMode = newValue
                }
            }
        }
        .navigationViewStyle(StackNavigationViewStyle())
        .accentColor(themeManager.colors.primary)
    }
    
    private func loadCurrentSettings() {
        degreeName = appSettings.degreeName
        totalCredits = appSettings.totalCredits
        maxGrade = appSettings.maxGrade
        passThreshold = appSettings.passThreshold
        targetAverage = appSettings.targetAverage
        isDarkMode = appSettings.isDarkMode
    }
    
    private func saveSettings() {
        // Validate settings
        if passThreshold > maxGrade {
            errorMessage = NSLocalizedString("Pass threshold cannot be greater than maximum grade.", comment: "Error message")
            showingErrorMessage = true
            return
        }
        
        // Update app settings
        appSettings.degreeName = degreeName
        appSettings.totalCredits = totalCredits
        appSettings.maxGrade = maxGrade
        appSettings.passThreshold = passThreshold
        appSettings.targetAverage = targetAverage
        appSettings.isDarkMode = isDarkMode
        
        // Show success message
        successMessage = NSLocalizedString("Your settings have been saved successfully.", comment: "Success message")
        showingSuccessMessage = true
    }
    
    private func handleExport(result: Result<URL, Error>) {
        switch result {
        case .success:
            successMessage = NSLocalizedString("Data exported successfully.", comment: "Success message")
            showingSuccessMessage = true
        case .failure(let error):
            errorMessage = NSLocalizedString("Failed to export data: ", comment: "Error message") + error.localizedDescription
            showingErrorMessage = true
        }
    }
    
    private func handleImport(result: Result<[URL], Error>) {
        switch result {
        case .success(let urls):
            guard let selectedFile = urls.first else { return }
            
            do {
                // Copy selected file to app's documents directory
                let documentsDirectory = try FileManager.default.url(
                    for: .documentDirectory,
                    in: .userDomainMask,
                    appropriateFor: nil,
                    create: true
                )
                
                let destinationURL = documentsDirectory.appendingPathComponent("university_tracker_import.db")
                
                if FileManager.default.fileExists(atPath: destinationURL.path) {
                    try FileManager.default.removeItem(at: destinationURL)
                }
                
                try FileManager.default.copyItem(at: selectedFile, to: destinationURL)
                
                successMessage = NSLocalizedString("Data imported successfully. Please restart the application.", comment: "Success message")
                showingSuccessMessage = true
            } catch {
                errorMessage = NSLocalizedString("Failed to import data: ", comment: "Error message") + error.localizedDescription
                showingErrorMessage = true
            }
            
        case .failure(let error):
            errorMessage = NSLocalizedString("Failed to import data: ", comment: "Error message") + error.localizedDescription
            showingErrorMessage = true
        }
    }
    
    private func resetData() {
        // Delete all exams
        let examsFetchRequest: NSFetchRequest<NSFetchRequestResult> = ExamEntity.fetchRequest()
        let examsDeleteRequest = NSBatchDeleteRequest(fetchRequest: examsFetchRequest)
        
        // Delete all events
        let eventsFetchRequest: NSFetchRequest<NSFetchRequestResult> = EventEntity.fetchRequest()
        let eventsDeleteRequest = NSBatchDeleteRequest(fetchRequest: eventsFetchRequest)
        
        // Delete all settings
        let settingsFetchRequest: NSFetchRequest<NSFetchRequestResult> = SettingEntity.fetchRequest()
        let settingsDeleteRequest = NSBatchDeleteRequest(fetchRequest: settingsFetchRequest)
        
        do {
            try viewContext.execute(examsDeleteRequest)
            try viewContext.execute(eventsDeleteRequest)
            try viewContext.execute(settingsDeleteRequest)
            
            // Reset app settings to default
            appSettings.resetSettings()
            
            // Reload values
            loadCurrentSettings()
            
            // Show success message
            successMessage = NSLocalizedString("All data has been reset to default.", comment: "Success message")
            showingSuccessMessage = true
        } catch {
            errorMessage = NSLocalizedString("Failed to reset data: ", comment: "Error message") + error.localizedDescription
            showingErrorMessage = true
        }
    }
}

// Simple document class for database export
class DatabaseDocument: FileDocument {
    static var readableContentTypes: [UTType] { [UTType.database] }
    
    init() {}
    
    required init(configuration: ReadConfiguration) throws {
        // Not needed for export
    }
    
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        // Get the database file path
        guard let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            throw NSError(domain: "AppError", code: 1, userInfo: [NSLocalizedDescriptionKey: "Could not access documents directory"])
        }
        
        let dbPath = documentsDirectory.appendingPathComponent("CoreDataModel.sqlite")
        
        // Check if the file exists
        guard FileManager.default.fileExists(atPath: dbPath.path) else {
            throw NSError(domain: "AppError", code: 2, userInfo: [NSLocalizedDescriptionKey: "Database file does not exist"])
        }
        
        // Read the file data
        let data = try Data(contentsOf: dbPath)
        
        // Create and return a file wrapper
        return FileWrapper(regularFileWithContents: data)
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
            .environmentObject(AppSettings())
            .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
    }
}
