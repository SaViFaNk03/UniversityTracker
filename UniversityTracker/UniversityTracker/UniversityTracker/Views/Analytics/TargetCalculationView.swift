import SwiftUI
import Combine

struct TargetCalculationView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @EnvironmentObject private var appSettings: AppSettings
    
    @State private var calculationMode: CalculationMode = .auto
    @State private var targetAverage: Int = 100
    @State private var exams: [Exam] = []
    @State private var passedExams: [Exam] = []
    @State private var plannedExams: [Exam] = []
    @State private var requiredGrades: [UUID: Double] = [:]
    @State private var fixedGrades: [UUID: Double] = [:]
    @State private var selectedExam: Exam? = nil
    @State private var showingGradeEditor = false
    
    private let calculator = AcademicCalculator()
    
    enum CalculationMode: String, CaseIterable {
        case auto = "auto"
        case manual = "manual"
        
        var localizedName: String {
            switch self {
            case .auto:
                return NSLocalizedString("Auto Mode", comment: "Target calculation mode")
            case .manual:
                return NSLocalizedString("Manual Mode", comment: "Target calculation mode")
            }
        }
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Target parameters section
                GroupBox(label: Text(NSLocalizedString("Target Parameters", comment: "Section title")).font(.headline)) {
                    VStack(spacing: 16) {
                        // Target average input
                        Stepper(value: $targetAverage, in: 18...110) {
                            HStack {
                                Text(NSLocalizedString("Target Average (scale 110)", comment: "Field label"))
                                Spacer()
                                Text("\(targetAverage)")
                                    .foregroundColor(.secondary)
                            }
                        }
                        
                        // Mode selection
                        HStack {
                            Text(NSLocalizedString("Mode", comment: "Field label"))
                            
                            Picker("", selection: $calculationMode) {
                                ForEach(CalculationMode.allCases, id: \.self) { mode in
                                    Text(mode.localizedName).tag(mode)
                                }
                            }
                            .pickerStyle(SegmentedPickerStyle())
                            .onChange(of: calculationMode) { oldMode, newMode in
                                if newMode == .auto {
                                    calculateTargets()
                                }
                            }
                        }
                        
                        Button(action: calculateTargets) {
                            Text(NSLocalizedString("Calculate", comment: "Button title"))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 8)
                        }
                        .buttonStyle(BorderedButtonStyle())
                        
                        if !fixedGrades.isEmpty {
                            Button(action: resetAllFixedGrades) {
                                Text(NSLocalizedString("Reset All Auto Grades", comment: "Button title"))
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 8)
                            }
                            .buttonStyle(BorderedButtonStyle())
                        }
                        
                        // Instructions based on mode
                        if calculationMode == .auto {
                            Text(NSLocalizedString("Double-click on a grade in the table to edit it manually. Other grades will be recalculated automatically.", comment: "Instructions"))
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                                .padding(.top, 8)
                        } else {
                            Text(NSLocalizedString("Freely modify grades to see how they affect your final average.", comment: "Instructions"))
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                                .padding(.top, 8)
                        }
                    }
                    .padding()
                }
                .padding(.horizontal)
                
                // Results section
                VStack(alignment: .leading, spacing: 8) {
                    Text(NSLocalizedString("Required Grades for Target", comment: "Section title"))
                        .font(.headline)
                        .padding(.horizontal)
                    
                    if plannedExams.isEmpty {
                        Text(NSLocalizedString("No planned exams to calculate required grades", comment: "Empty state message"))
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding()
                    } else {
                        // Results table
                        ForEach(plannedExams) { exam in
                            RequiredGradeRow(
                                exam: exam,
                                requiredGrade: requiredGrades[exam.id] ?? 0,
                                isFixed: isGradeFixed(for: exam.id),
                                isManualMode: calculationMode == .manual,
                                onGradeChange: { newGrade in
                                    updateGrade(for: exam.id, newGrade: newGrade)
                                },
                                onTap: {
                                    if calculationMode == .auto {
                                        selectedExam = exam
                                        showingGradeEditor = true
                                    }
                                }
                            )
                            .padding(.horizontal)
                            .padding(.vertical, 4)
                            .background(Color.secondaryBackground)
                            .cornerRadius(10)
                            .padding(.horizontal)
                        }
                    }
                    
                    // Summary
                    if !plannedExams.isEmpty {
                        HStack {
                            Text(NSLocalizedString("Projected Weighted Average", comment: "Result summary"))
                                .fontWeight(.bold)
                            
                            Spacer()
                            
                            Text(String(format: "%.2f", calculateProjectedAverage()))
                                .fontWeight(.bold)
                        }
                        .padding()
                        .background(Color.tertiaryBackground)
                        .cornerRadius(10)
                        .padding(.horizontal)
                    }
                }
            }
            .padding(.vertical)
        }
        .sheet(isPresented: $showingGradeEditor) {
            if let exam = selectedExam {
                GradeEditorView(
                    exam: exam,
                    currentGrade: requiredGrades[exam.id] ?? Double(appSettings.passThreshold),
                    maxGrade: Double(appSettings.maxGrade),
                    minGrade: Double(appSettings.passThreshold),
                    onSave: { newGrade in
                        if newGrade < 0 {
                            // Reset this fixed grade
                            fixedGrades.removeValue(forKey: exam.id)
                        } else {
                            // Set a fixed grade
                            fixedGrades[exam.id] = newGrade
                        }
                        calculateTargets()
                    }
                )
            }
        }
        .onAppear {
            loadExams()
            targetAverage = appSettings.targetAverage
            calculateTargets()
        }
    }
    
    private func loadExams() {
        exams = Exam.getAllExams(context: viewContext)
        passedExams = exams.filter { $0.status == .passed }
        plannedExams = exams.filter { $0.status == .planned }
        
        // Initialize required grades
        for exam in plannedExams {
            if requiredGrades[exam.id] == nil {
                requiredGrades[exam.id] = Double(appSettings.passThreshold)
            }
        }
    }
    
    private func calculateTargets() {
        guard !plannedExams.isEmpty else { return }
        
        let targetAvg = (Double(targetAverage) / 110.0) * Double(appSettings.maxGrade)
        
        requiredGrades = calculator.calculateRequiredGrades(
            allExams: exams,
            plannedExams: plannedExams,
            targetAverage: targetAvg,
            maxGrade: appSettings.maxGrade,
            fixedGrades: fixedGrades
        )
    }
    
    private func isGradeFixed(for examId: UUID) -> Bool {
        return fixedGrades[examId] != nil
    }
    
    private func updateGrade(for examId: UUID, newGrade: Double) {
        requiredGrades[examId] = newGrade
        
        if calculationMode == .manual {
            // In manual mode, we always consider modified grades as fixed
            fixedGrades[examId] = newGrade
        } else {
            // In auto mode, recalculate other grades
            calculateTargets()
        }
    }
    
    private func resetAllFixedGrades() {
        fixedGrades.removeAll()
        calculateTargets()
    }
    
    private func calculateProjectedAverage() -> Double {
        // Combine passed exams with planned exams using required grades
        var totalWeightedSum = 0.0
        var totalCredits = 0
        
        // Include passed exams
        for exam in passedExams {
            if let grade = exam.grade {
                totalWeightedSum += grade * Double(exam.credits)
                totalCredits += exam.credits
            }
        }
        
        // Include planned exams with their required grades
        for exam in plannedExams {
            if let grade = requiredGrades[exam.id] {
                totalWeightedSum += grade * Double(exam.credits)
                totalCredits += exam.credits
            }
        }
        
        // Calculate and convert to 110 scale
        if totalCredits > 0 {
            let weightedAvg = totalWeightedSum / Double(totalCredits)
            return calculator.convertTo110Scale(grade: weightedAvg, maxGrade: appSettings.maxGrade)
        }
        
        return 0.0
    }
}

struct RequiredGradeRow: View {
    var exam: Exam
    var requiredGrade: Double
    var isFixed: Bool
    var isManualMode: Bool
    var onGradeChange: (Double) -> Void
    var onTap: () -> Void
    
    @State private var localGrade: Double
    
    init(exam: Exam, requiredGrade: Double, isFixed: Bool, isManualMode: Bool, 
         onGradeChange: @escaping (Double) -> Void, onTap: @escaping () -> Void) {
        self.exam = exam
        self.requiredGrade = requiredGrade
        self.isFixed = isFixed
        self.isManualMode = isManualMode
        self.onGradeChange = onGradeChange
        self.onTap = onTap
        
        // Initialize the local state
        _localGrade = State(initialValue: requiredGrade)
    }
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(exam.name)
                    .font(.headline)
                
                Text("\(exam.credits) CFU")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            if isManualMode {
                // In manual mode, show a stepper
                Stepper(value: $localGrade, in: 18...30, step: 0.5) {
                    Text(String(format: "%.1f", localGrade))
                        .font(.headline)
                        .foregroundColor(isFixed ? .blue : .primary)
                        .frame(minWidth: 40, alignment: .trailing)
                }
                .onChange(of: localGrade) { oldValue, newValue in
                    onGradeChange(newValue)
                }
            } else {
                // In auto mode, show the calculated grade
                Text(String(format: "%.1f", requiredGrade))
                    .font(.headline)
                    .foregroundColor(isFixed ? .blue : .primary)
                    .frame(minWidth: 40, alignment: .trailing)
            }
        }
        .padding(.vertical, 8)
        .contentShape(Rectangle())
        .onTapGesture {
            if !isManualMode {
                onTap()
            }
        }
        .onChange(of: requiredGrade) { oldValue, newValue in
            // Update our local value if external value changes
            localGrade = newValue
        }
    }
}

struct GradeEditorView: View {
    var exam: Exam
    var currentGrade: Double
    var maxGrade: Double
    var minGrade: Double
    var onSave: (Double) -> Void
    
    @Environment(\.dismiss) private var dismiss
    @State private var grade: Double
    
    init(exam: Exam, currentGrade: Double, maxGrade: Double, minGrade: Double, onSave: @escaping (Double) -> Void) {
        self.exam = exam
        self.currentGrade = currentGrade
        self.maxGrade = maxGrade
        self.minGrade = minGrade
        self.onSave = onSave
        
        // Initialize state
        _grade = State(initialValue: currentGrade)
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text(NSLocalizedString("Set Target Grade", comment: "Form section"))) {
                    Text("You are manually setting the target grade for '\(exam.name)'. Other grades will be recalculated automatically to maintain the target average.")
                        .font(.callout)
                        .foregroundColor(.secondary)
                        .padding(.vertical, 8)
                    
                    Stepper(value: $grade, in: minGrade...maxGrade, step: 0.5) {
                        HStack {
                            Text(NSLocalizedString("Target Grade", comment: "Form field"))
                            Spacer()
                            Text(String(format: "%.1f", grade))
                                .foregroundColor(.blue)
                        }
                    }
                }
                
                Section {
                    Button {
                        onSave(grade)
                        dismiss()
                    } label: {
                        Text(NSLocalizedString("Save", comment: "Button"))
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                    
                    Button {
                        onSave(-1) // Special value to indicate reset
                        dismiss()
                    } label: {
                        Text(NSLocalizedString("Reset to Automatic Calculation", comment: "Button"))
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                    .foregroundColor(.red)
                }
                
                Section {
                    Button {
                        dismiss()
                    } label: {
                        Text(NSLocalizedString("Cancel", comment: "Button"))
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                    .foregroundColor(.secondary)
                }
            }
            .navigationTitle(NSLocalizedString("Set Target Grade", comment: "Navigation title"))
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct TargetCalculationView_Previews: PreviewProvider {
    static var previews: some View {
        TargetCalculationView()
            .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
            .environmentObject(AppSettings())
    }
}
