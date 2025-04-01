import SwiftUI
import Charts

struct BarChartView: View {
    var exams: [Exam]
    var maxGrade: Int
    
    private var minGrade: Int {
        return 18 // Minimum passing grade in Italian system
    }
    
    private struct GradeData: Identifiable {
        let id = UUID()
        let grade: Int
        let count: Int
    }
    
    private var data: [GradeData] {
        // Count exams for each grade
        var countByGrade: [Int: Int] = [:]
        
        for grade in minGrade...maxGrade {
            countByGrade[grade] = 0
        }
        
        for exam in exams {
            if let grade = exam.grade, exam.status == .passed {
                let roundedGrade = Int(grade.rounded())
                countByGrade[roundedGrade, default: 0] += 1
            }
        }
        
        // Convert to array for chart
        return countByGrade.map { GradeData(grade: $0.key, count: $0.value) }
            .sorted { $0.grade < $1.grade }
    }
    
    var body: some View {
        if #available(iOS 16.0, *) {
            if data.isEmpty {
                Text(NSLocalizedString("No grades to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Chart(data) { item in
                    BarMark(
                        x: .value(NSLocalizedString("Grade", comment: "Chart x-axis"), item.grade),
                        y: .value(NSLocalizedString("Count", comment: "Chart y-axis"), item.count)
                    )
                    .foregroundStyle(.blue)
                    .cornerRadius(5)
                }
                .chartXScale(domain: minGrade...maxGrade)
                .chartYScale(domain: 0...max(1, data.map { $0.count }.max() ?? 0))
                .chartXAxis {
                    AxisMarks(values: .stride(by: 1)) { value in
                        if let grade = value.as(Int.self), grade % 2 == 0 {
                            AxisValueLabel()
                        }
                    }
                }
            }
        } else {
            // Fallback for iOS 15
            if data.isEmpty {
                Text(NSLocalizedString("No grades to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                GeometryReader { geometry in
                    HStack(alignment: .bottom, spacing: 4) {
                        ForEach(data) { item in
                            VStack {
                                Rectangle()
                                    .fill(Color.blue)
                                    .frame(height: item.count > 0 ? CGFloat(item.count) / CGFloat(maxCount()) * geometry.size.height * 0.8 : 2)
                                    .cornerRadius(4)
                                
                                if item.grade % 2 == 0 {
                                    Text("\(item.grade)")
                                        .font(.caption2)
                                        .rotationEffect(.degrees(-45))
                                        .fixedSize()
                                } else {
                                    Spacer()
                                        .frame(height: 15)
                                }
                            }
                        }
                    }
                    .padding(.bottom, 15)
                    .padding(.top, 10)
                }
            }
        }
    }
    
    // Helper for iOS 15 fallback
    private func maxCount() -> Int {
        return max(1, data.map { $0.count }.max() ?? 0)
    }
}

struct BarChartView_Previews: PreviewProvider {
    static var previews: some View {
        let exams: [Exam] = [
            Exam(name: "Exam 1", credits: 6, status: .passed, grade: 25),
            Exam(name: "Exam 2", credits: 9, status: .passed, grade: 28),
            Exam(name: "Exam 3", credits: 6, status: .passed, grade: 25),
            Exam(name: "Exam 4", credits: 12, status: .passed, grade: 30)
        ]
        
        BarChartView(exams: exams, maxGrade: 30)
            .frame(height: 200)
            .padding()
            .previewLayout(.sizeThatFits)
    }
}
