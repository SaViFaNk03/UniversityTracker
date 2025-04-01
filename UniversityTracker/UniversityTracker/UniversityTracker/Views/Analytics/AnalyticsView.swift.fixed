import SwiftUI
import Charts

struct AnalyticsView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationView {
            VStack {
                Picker(NSLocalizedString("Analysis Type", comment: "Analytics tab picker"), selection: $selectedTab) {
                    Text(NSLocalizedString("Target Grades", comment: "Analytics tab option"))
                        .tag(0)
                    
                    Text(NSLocalizedString("Trends", comment: "Analytics tab option"))
                        .tag(1)
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)
                
                if selectedTab == 0 {
                    TargetCalculationView()
                } else {
                    TrendsView()
                }
            }
            .navigationTitle(NSLocalizedString("Analytics", comment: "Analytics title"))
        }
    }
}

struct TrendsView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @EnvironmentObject private var appSettings: AppSettings
    @State private var passedExams: [Exam] = []
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Grades trend chart
                VStack(alignment: .leading, spacing: 10) {
                    Text(NSLocalizedString("Grade Trends", comment: "Trends chart title"))
                        .font(.headline)
                        .padding(.horizontal)
                    
                    LineChartView(
                        exams: passedExams,
                        title: NSLocalizedString("Grades", comment: "Chart title"),
                        yLabel: NSLocalizedString("Grade", comment: "Chart y-axis")
                    )
                    .frame(height: 250)
                    .padding()
                    .background(Color.secondaryBackground)
                    .cornerRadius(10)
                    .padding(.horizontal)
                }
                
                // Credits accumulation chart
                VStack(alignment: .leading, spacing: 10) {
                    Text(NSLocalizedString("Credits Accumulation", comment: "Trends chart title"))
                        .font(.headline)
                        .padding(.horizontal)
                    
                    CumulativeCreditsChartView(exams: passedExams)
                        .frame(height: 250)
                        .padding()
                        .background(Color.secondaryBackground)
                        .cornerRadius(10)
                        .padding(.horizontal)
                }
            }
            .padding(.vertical)
        }
        .onAppear {
            loadExams()
        }
    }
    
    private func loadExams() {
        passedExams = Exam.getExams(withStatus: .passed, context: viewContext)
            .sorted { ($0.date ?? Date.distantPast) < ($1.date ?? Date.distantPast) }
    }
}

struct LineChartView: View {
    var exams: [Exam]
    var title: String
    var yLabel: String
    
    private struct ChartData: Identifiable {
        let id = UUID()
        let index: Int
        let date: Date
        let value: Double
        let cumulative: Double
    }
    
    private var chartData: [ChartData] {
        let validExams = exams.filter { $0.grade != nil && $0.date != nil }
            .sorted { ($0.date ?? Date.distantPast) < ($1.date ?? Date.distantPast) }
        
        var cumulativeSum = 0.0
        
        return validExams.enumerated().map { index, exam in
            cumulativeSum += exam.grade ?? 0
            let average = cumulativeSum / Double(index + 1)
            
            return ChartData(
                index: index,
                date: exam.date ?? Date(),
                value: exam.grade ?? 0,
                cumulative: average
            )
        }
    }
    
    var body: some View {
        if #available(iOS 16.0, *) {
            if chartData.isEmpty {
                Text(NSLocalizedString("No data to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Chart {
                    ForEach(chartData) { item in
                        LineMark(
                            x: .value(NSLocalizedString("Exam", comment: "Chart x-axis"), String(item.index)),
                            y: .value(yLabel, item.value)
                        )
                        .foregroundStyle(.blue)
                        .symbol(Circle().strokeBorder(lineWidth: 2.0))
                    }
                    
                    ForEach(chartData) { item in
                        LineMark(
                            x: .value(NSLocalizedString("Exam", comment: "Chart x-axis"), String(item.index)),
                            y: .value(NSLocalizedString("Cumulative Average", comment: "Chart line"), item.cumulative)
                        )
                        .foregroundStyle(.red)
                        .lineStyle(StrokeStyle(lineWidth: 2.0, dash: [5.0, 5.0]))
                    }
                }
                .chartXAxis {
                    AxisMarks(position: .bottom, values: .automatic(desiredCount: min(10, chartData.count))) { value in
                        if let index = value.as(Int.self), index < chartData.count {
                            AxisValueLabel {
                                Text(DateFormatter.shortDate.string(from: chartData[index].date))
                                    .font(.caption)
                                    .rotationEffect(.degrees(-45))
                            }
                        }
                    }
                }
            }
        } else {
            // Fallback for iOS 15
            if chartData.isEmpty {
                Text(NSLocalizedString("No data to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                // Simple line chart for iOS 15
                GeometryReader { geometry in
                    ZStack {
                        // Y-axis
                        Rectangle()
                            .fill(Color.secondary)
                            .frame(width: 1)
                            .offset(x: 40, y: 0)
                        
                        // X-axis
                        Rectangle()
                            .fill(Color.secondary)
                            .frame(height: 1)
                            .offset(x: 0, y: geometry.size.height - 40)
                        
                        // Line and points
                        Path { path in
                            let width = geometry.size.width - 80
                            let height = geometry.size.height - 80
                            let maxValue = chartData.map { $0.value }.max() ?? 30
                            let minValue = chartData.map { $0.value }.min() ?? 18
                            let range = maxValue - minValue
                            
                            for (index, item) in chartData.enumerated() {
                                let x = 40 + (CGFloat(index) / CGFloat(chartData.count - 1)) * width
                                let y = geometry.size.height - 40 - ((item.value - minValue) / range) * height
                                
                                if index == 0 {
                                    path.move(to: CGPoint(x: x, y: y))
                                } else {
                                    path.addLine(to: CGPoint(x: x, y: y))
                                }
                            }
                        }
                        .stroke(Color.blue, lineWidth: 2)
                        
                        // Points
                        ForEach(chartData) { item in
                            let width = geometry.size.width - 80
                            let height = geometry.size.height - 80
                            let maxValue = chartData.map { $0.value }.max() ?? 30
                            let minValue = chartData.map { $0.value }.min() ?? 18
                            let range = maxValue - minValue
                            
                            let x = 40 + (CGFloat(item.index) / CGFloat(chartData.count - 1)) * width
                            let y = geometry.size.height - 40 - ((item.value - minValue) / range) * height
                            
                            Circle()
                                .fill(Color.white)
                                .frame(width: 8, height: 8)
                                .overlay(Circle().stroke(Color.blue, lineWidth: 2))
                                .position(x: x, y: y)
                        }
                    }
                }
            }
        }
    }
}

struct CumulativeCreditsChartView: View {
    var exams: [Exam]
    
    private struct ChartData: Identifiable {
        let id = UUID()
        let index: Int
        let date: Date
        let cumulativeCredits: Int
    }
    
    private var chartData: [ChartData] {
        let validExams = exams.filter { $0.date != nil }
            .sorted { ($0.date ?? Date.distantPast) < ($1.date ?? Date.distantPast) }
        
        var cumulativeCredits = 0
        
        return validExams.enumerated().map { index, exam in
            cumulativeCredits += exam.credits
            
            return ChartData(
                index: index,
                date: exam.date ?? Date(),
                cumulativeCredits: cumulativeCredits
            )
        }
    }
    
    var body: some View {
        if #available(iOS 16.0, *) {
            if chartData.isEmpty {
                Text(NSLocalizedString("No data to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Chart {
                    ForEach(chartData) { item in
                        LineMark(
                            x: .value(NSLocalizedString("Exam", comment: "Chart x-axis"), String(item.index)),
                            y: .value(NSLocalizedString("Credits", comment: "Chart y-axis"), item.cumulativeCredits)
                        )
                        .foregroundStyle(.green)
                        .symbol(Circle().strokeBorder(lineWidth: 2.0))
                    }
                    
                    ForEach(chartData) { item in
                        AreaMark(
                            x: .value(NSLocalizedString("Exam", comment: "Chart x-axis"), String(item.index)),
                            y: .value(NSLocalizedString("Credits", comment: "Chart y-axis"), item.cumulativeCredits)
                        )
                        .foregroundStyle(.green.opacity(0.2))
                    }
                }
                .chartXAxis {
                    AxisMarks(position: .bottom, values: .automatic(desiredCount: min(10, chartData.count))) { value in
                        if let index = value.as(Int.self), index < chartData.count {
                            AxisValueLabel {
                                Text(DateFormatter.shortDate.string(from: chartData[index].date))
                                    .font(.caption)
                                    .rotationEffect(.degrees(-45))
                            }
                        }
                    }
                }
            }
        } else {
            // Fallback for iOS 15
            if chartData.isEmpty {
                Text(NSLocalizedString("No data to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                // Simple chart fallback
                Text("Credits accumulated over time: \(chartData.last?.cumulativeCredits ?? 0)")
                    .foregroundColor(.secondary)
            }
        }
    }
}

struct AnalyticsView_Previews: PreviewProvider {
    static var previews: some View {
        AnalyticsView()
            .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
            .environmentObject(AppSettings())
    }
}