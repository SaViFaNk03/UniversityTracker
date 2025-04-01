import SwiftUI

struct ExamFormView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @EnvironmentObject private var appSettings: AppSettings
    @Environment(\.dismiss) private var dismiss
    
    var exam: Exam?
    var onSave: (Exam) -> Void
    
    @State private var name: String = ""
    @State private var credits: Int = 6
    @State private var status: ExamStatus = .planned
    @State private var grade: Double = 18
    @State private var date: Date = Date()
    @State private var notes: String = ""
    
    var body: some View {
        Form {
            Section(header: Text("Exam Details")) {
                TextField(NSLocalizedString("Exam Name", comment: "Form field"), text: $name)
                
                Stepper("\(NSLocalizedString("Credits", comment: "Form field")): \(credits) CFU", value: $credits, in: 1...30)
                
                Picker(NSLocalizedString("Status", comment: "Form field"), selection: $status) {
                    ForEach(ExamStatus.allCases) { status in
                        Text(status.localizedName).tag(status)
                    }
                }
                
                if status == .passed {
                    Stepper(value: $grade, in: Double(appSettings.passThreshold)...Double(appSettings.maxGrade), step: 0.5) {
                        HStack {
                            Text(NSLocalizedString("Grade", comment: "Form field"))
                            Spacer()
                            Text("\(grade, specifier: "%.1f")")
                        }
                    }
                }
                
                DatePicker(NSLocalizedString("Date", comment: "Form field"), selection: $date, displayedComponents: .date)
            }
            
            Section(header: Text(NSLocalizedString("Notes", comment: "Form field"))) {
                TextEditor(text: $notes)
                    .frame(minHeight: 100)
            }
            
            Section {
                Button {
                    saveExam()
                } label: {
                    Text(NSLocalizedString("Save", comment: "Save button"))
                        .frame(maxWidth: .infinity)
                        .foregroundColor(.white)
                }
                .listRowBackground(Color.blue)
            }
        }
        .onAppear {
            if let exam = exam {
                name = exam.name
                credits = exam.credits
                status = exam.status
                grade = exam.grade ?? Double(appSettings.passThreshold)
                date = exam.date ?? Date()
                notes = exam.notes ?? ""
            }
        }
    }
    
    private func saveExam() {
        // Create or update exam
        let savedExam = Exam(
            id: exam?.id ?? UUID(),
            name: name,
            credits: credits,
            status: status,
            grade: status == .passed ? grade : nil,
            date: date,
            notes: notes
        )
        
        savedExam.save(in: viewContext)
        onSave(savedExam)
    }
}

struct ExamFormView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            ExamFormView(exam: nil) { _ in }
                .environmentObject(AppSettings())
        }
    }
}
