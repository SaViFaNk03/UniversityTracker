import SwiftUI

struct PieSliceView: View {
    var startAngle: Double
    var endAngle: Double
    var color: Color
    
    var body: some View {
        GeometryReader { geometry in
            Path { path in
                let center = CGPoint(x: geometry.size.width / 2, y: geometry.size.height / 2)
                let radius = min(geometry.size.width, geometry.size.height) / 2
                
                path.move(to: center)
                path.addArc(
                    center: center,
                    radius: radius,
                    startAngle: .degrees(startAngle - 90),
                    endAngle: .degrees(endAngle - 90),
                    clockwise: false
                )
                path.closeSubpath()
            }
            .fill(color)
        }
    }
}

// Helper functions for iOS 15 fallback
func startAngle(for index: Int, data: [ChartData]) -> Double {
    let total = data.reduce(0) { accumulator, current in
        accumulator + current.count
    }
    
    let startPercent = Double(data.prefix(index).reduce(0) { accumulator, current in
        accumulator + current.count
    }) / Double(total)
    
    return startPercent * 360.0
}

func endAngle(for index: Int, data: [ChartData]) -> Double {
    let total = data.reduce(0) { accumulator, current in
        accumulator + current.count
    }
    
    let endPercent = Double(data.prefix(index + 1).reduce(0) { accumulator, current in
        accumulator + current.count
    }) / Double(total)
    
    return endPercent * 360.0
}

// Fixing the function that has errors in the image
struct ChartData: Identifiable {
    let id = UUID()
    let status: String
    let count: Int
    let color: Color
}

// Specific fix for function shown in the image
func startAngleFixed(for index: Int, data: [ChartData]) -> Double {
    let total = data.reduce(0) { accumulator, current in
        accumulator + current.count
    }
    
    let startPercent = Double(data.prefix(index).reduce(0) { accumulator, current in
        accumulator + current.count
    }) / Double(total)
    
    return startPercent * 360.0
}

// Format example from the image:
// Helper functions for iOS 15 fallback
func startAngleFormat() {
    // let total = data.reduce(0) { accumulator, current in accumulator + current.count }
    // let startPercent = Double(data.prefix(index).reduce(0) { accumulator, current in accumulator + current.count }) / Double(total)
    let index = 0
    let total = 100 
    
    // Using Date extensions for prefix + reduce examples:
    let dates = [Date()]
    let endPercent = Double(dates.prefix(index + 1).reduce(0) { accumulator, current in
        accumulator + current.timeIntervalSince1970
    }) / Double(total)
}