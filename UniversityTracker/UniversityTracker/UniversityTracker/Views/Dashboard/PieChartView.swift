import SwiftUI
import Charts

struct PieChartView: View {
    var passedCount: Int
    var failedCount: Int
    var plannedCount: Int
    
    private struct ChartData: Identifiable {
        let id = UUID()
        let status: String
        let count: Int
        let color: Color
    }
    
    private var data: [ChartData] {
        var result: [ChartData] = []
        
        if passedCount > 0 {
            result.append(ChartData(
                status: NSLocalizedString("Passed", comment: "Exam status"),
                count: passedCount,
                color: .statusPassed
            ))
        }
        
        if failedCount > 0 {
            result.append(ChartData(
                status: NSLocalizedString("Failed", comment: "Exam status"),
                count: failedCount,
                color: .statusFailed
            ))
        }
        
        if plannedCount > 0 {
            result.append(ChartData(
                status: NSLocalizedString("Planned", comment: "Exam status"),
                count: plannedCount,
                color: .statusPlanned
            ))
        }
        
        return result
    }
    
    var body: some View {
        if #available(iOS 16.0, *) {
            if data.isEmpty {
                Text(NSLocalizedString("No exams to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Chart(data) { item in
                    SectorMark(
                        angle: .value(NSLocalizedString("Count", comment: "Chart value"), item.count),
                        innerRadius: .ratio(0.2),
                        angularInset: 1.5
                    )
                    .foregroundStyle(item.color)
                    .cornerRadius(5)
                    .annotation(position: .overlay) {
                        Text("\(item.count)")
                            .font(.caption)
                            .foregroundColor(.white)
                            .fontWeight(.bold)
                    }
                }
                .chartLegend(position: .bottom, alignment: .center, spacing: 20)
            }
        } else {
            // Fallback for iOS 15
            if data.isEmpty {
                Text(NSLocalizedString("No exams to display", comment: "Empty chart message"))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                VStack {
                    // Simple pie chart implementation for iOS 15
                    ZStack {
                        ForEach(0..<data.count, id: \.self) { index in
                            PieSliceView(
                                startAngle: startAngle(for: index),
                                endAngle: endAngle(for: index),
                                color: data[index].color
                            )
                        }
                        
                        // Inner circle for donut chart
                        Circle()
                            .fill(Color.background)
                            .frame(width: 60, height: 60)
                    }
                    
                    // Legend
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(data) { item in
                            HStack {
                                Rectangle()
                                    .fill(item.color)
                                    .frame(width: 16, height: 16)
                                    .cornerRadius(4)
                                
                                Text("\(item.status): \(item.count)")
                                    .font(.caption)
                            }
                        }
                    }
                    .padding(.top)
                }
            }
        }
    }
    
    // Helper functions for iOS 15 fallback
    private func startAngle(for index: Int) -> Double {
        let total = data.reduce(0) { accumulator, current in
            accumulator + current.count
        }
        
        let startPercent = Double(data.prefix(index).reduce(0) { accumulator, current in
            accumulator + current.count
        }) / Double(total)
        
        return startPercent * 360.0
    }
    
    private func endAngle(for index: Int) -> Double {
        let total = data.reduce(0) { accumulator, current in
            accumulator + current.count
        }
        
        let endPercent = Double(data.prefix(index + 1).reduce(0) { accumulator, current in
            accumulator + current.count
        }) / Double(total)
        
        return endPercent * 360.0
    }
}

// Simple pie slice for iOS 15 fallback


struct PieChartView_Previews: PreviewProvider {
    static var previews: some View {
        PieChartView(passedCount: 10, failedCount: 2, plannedCount: 5)
            .frame(height: 200)
            .padding()
            .previewLayout(.sizeThatFits)
    }
}
