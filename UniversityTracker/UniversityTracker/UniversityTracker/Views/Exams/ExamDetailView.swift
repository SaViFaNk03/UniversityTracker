import SwiftUI

struct ExamDetailView: View {
    var exam: Exam
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Status badge
                StatusBadge(status: exam.status)
                    .padding(.bottom, 4)
                
                // Basic info
                InfoRow(
                    title: NSLocalizedString("Credits", comment: "Exam detail"),
                    value: "\(exam.credits) CFU",
                    icon: "creditcard"
                )
                
                if let grade = exam.grade, exam.status == .passed {
                    InfoRow(
                        title: NSLocalizedString("Grade", comment: "Exam detail"),
                        value: "\(Int(grade))",
                        icon: "star.fill"
                    )
                }
                
                if let date = exam.date {
                    InfoRow(
                        title: NSLocalizedString("Date", comment: "Exam detail"),
                        value: DateFormatter.mediumDate.string(from: date),
                        icon: "calendar"
                    )
                }
                
                // Notes section
                if let notes = exam.notes, !notes.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(NSLocalizedString("Notes", comment: "Exam detail"))
                            .font(.headline)
                        
                        Text(notes)
                            .font(.body)
                            .padding()
                            .background(Color.secondaryBackground)
                            .cornerRadius(8)
                    }
                }
                
                Spacer()
            }
            .padding()
        }
        .navigationTitle(exam.name)
    }
}

struct InfoRow: View {
    var title: String
    var value: String
    var icon: String
    
    var body: some View {
        HStack {
            Label(title, systemImage: icon)
                .font(.headline)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .font(.body)
                .fontWeight(.medium)
        }
        .padding(.vertical, 4)
    }
}

struct ExamDetailView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            ExamDetailView(
                exam: Exam(
                    name: "Software Engineering",
                    credits: 9,
                    status: .passed,
                    grade: 28,
                    date: Date(),
                    notes: "Final project was about designing a mobile application. Group project with 4 people."
                )
            )
        }
    }
}
