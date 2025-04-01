import SwiftUI

struct StatCardView: View {
    var title: String
    var value: String
    
    var body: some View {
        VStack(spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            Text(value)
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(.primary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.secondaryBackground)
        .cornerRadius(10)
    }
}

struct StatCardView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            StatCardView(title: "Credits Earned", value: "60/180")
                .previewLayout(.sizeThatFits)
                .padding()
            
            StatCardView(title: "Average (110)", value: "98.78")
                .previewLayout(.sizeThatFits)
                .padding()
                .preferredColorScheme(.dark)
        }
    }
}
