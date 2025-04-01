import SwiftUI
import Charts

struct DashboardView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @EnvironmentObject private var appSettings: AppSettings
    @State private var exams: [Exam] = []
    @State private var calculator = AcademicCalculator()
    
    // Computed properties for statistics
    private var passedExams: [Exam] {
        exams.filter { $0.status == .passed }
    }
    
    private var failedExams: [Exam] {
        exams.filter { $0.status == .failed }
    }
    
    private var plannedExams: [Exam] {
        exams.filter { $0.status == .planned }
    }
    
    private var earnedCredits: Int {
        calculator.calculateTotalCredits(exams: exams)
    }
    
    private var simpleAverage: Double {
        calculator.calculateSimpleAverage(exams: exams)
    }
    
    private var weightedAverage: Double {
        calculator.calculateWeightedAverage(exams: exams)
    }
    
    private var progress: Double {
        calculator.calculateProgressPercentage(earnedCredits: earnedCredits, totalRequiredCredits: appSettings.totalCredits)
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Stats cards section
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        StatCardView(
                            title: NSLocalizedString("Credits Earned", comment: "Dashboard stat"),
                            value: "\(earnedCredits)/\(appSettings.totalCredits)"
                        )
                        
                        StatCardView(
                            title: NSLocalizedString("Average (110)", comment: "Dashboard stat"),
                            value: String(format: "%.2f", calculator.convertTo110Scale(grade: simpleAverage, maxGrade: appSettings.maxGrade))
                        )
                        
                        StatCardView(
                            title: NSLocalizedString("Weighted Average (110)", comment: "Dashboard stat"),
                            value: String(format: "%.2f", calculator.convertTo110Scale(grade: weightedAverage, maxGrade: appSettings.maxGrade))
                        )
                        
                        StatCardView(
                            title: NSLocalizedString("Exams Passed", comment: "Dashboard stat"),
                            value: "\(passedExams.count)"
                        )
                    }
                    .padding(.horizontal)
                    
                    // Progress section
                    VStack(alignment: .leading, spacing: 8) {
                        Text(NSLocalizedString("Progress Toward Degree", comment: "Progress bar title"))
                            .font(.headline)
                            .padding(.horizontal)
                        
                        ProgressView(value: progress, total: 100)
                            .progressViewStyle(LinearProgressViewStyle(tint: .green))
                            .padding(.horizontal)
                        
                        Text("\(Int(progress))% \(NSLocalizedString("completed", comment: "Progress bar label"))")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .padding(.horizontal)
                    }
                    
                    // Charts section
                    HStack {
                        VStack {
                            Text(NSLocalizedString("Exam Status", comment: "Pie chart title"))
                                .font(.headline)
                            
                            PieChartView(
                                passedCount: passedExams.count,
                                failedCount: failedExams.count,
                                plannedCount: plannedExams.count
                            )
                            .frame(height: 200)
                        }
                        .padding()
                        .background(Color.secondaryBackground)
                        .cornerRadius(10)
                        
                        VStack {
                            Text(NSLocalizedString("Grade Distribution", comment: "Bar chart title"))
                                .font(.headline)
                            
                            BarChartView(
                                exams: passedExams,
                                maxGrade: appSettings.maxGrade
                            )
                            .frame(height: 200)
                        }
                        .padding()
                        .background(Color.secondaryBackground)
                        .cornerRadius(10)
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle(NSLocalizedString("Overview", comment: "Dashboard title"))
            .onAppear {
                loadExams()
            }
        }
    }
    
    private func loadExams() {
        exams = Exam.getAllExams(context: viewContext)
    }
}

struct DashboardView_Previews: PreviewProvider {
    static var previews: some View {
        DashboardView()
            .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
            .environmentObject(AppSettings())
    }
}
