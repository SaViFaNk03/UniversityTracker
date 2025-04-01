import SwiftUI

struct EventFormView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss
    
    var event: Event?
    var date: Date
    var onSave: (Event) -> Void
    
    @State private var title = ""
    @State private var type = "personal"
    @State private var location = ""
    @State private var notes = ""
    @State private var startDate: Date = Date()
    @State private var endDate: Date = Date().addingTimeInterval(3600) // Default to 1 hour
    @State private var allDay = false
    @State private var color: Color = .blue
    @State private var relatedExam: Exam? = nil
    @State private var showingExamPicker = false
    
    private let eventTypes = ["personal", "exam", "study", "meeting", "other"]
    
    init(event: Event? = nil, date: Date = Date(), onSave: @escaping (Event) -> Void) {
        self.event = event
        self.date = date
        self.onSave = onSave
        
        // Initialize state properties
        _startDate = State(initialValue: event?.startDate ?? date)
        _endDate = State(initialValue: event?.endDate ?? date.addingTimeInterval(3600))
        _title = State(initialValue: event?.title ?? "")
        _type = State(initialValue: event?.type ?? "personal")
        _location = State(initialValue: event?.location ?? "")
        _notes = State(initialValue: event?.notes ?? "")
        _allDay = State(initialValue: event?.allDay ?? false)
        _color = State(initialValue: event?.color ?? .blue)
    }
    
    var body: some View {
        Form {
            Section(header: Text(NSLocalizedString("Event Details", comment: "Form section"))) {
                TextField(NSLocalizedString("Title", comment: "Form field"), text: $title)
                
                Picker(NSLocalizedString("Type", comment: "Form field"), selection: $type) {
                    ForEach(eventTypes, id: \.self) { type in
                        Text(NSLocalizedString(type.capitalized, comment: "Event type")).tag(type)
                    }
                }
                
                TextField(NSLocalizedString("Location", comment: "Form field"), text: $location)
                
                Toggle(NSLocalizedString("All Day", comment: "Form field"), isOn: $allDay)
                
                if !allDay {
                    DatePicker(NSLocalizedString("Start", comment: "Form field"), selection: $startDate)
                    
                    DatePicker(NSLocalizedString("End", comment: "Form field"), selection: $endDate)
                } else {
                    DatePicker(NSLocalizedString("Date", comment: "Form field"), selection: $startDate, displayedComponents: .date)
                }
                
                VStack(alignment: .leading) {
                    Text(NSLocalizedString("Color", comment: "Form field"))
                    ColorSelectionView(selectedColor: $color)
                }
                .padding(.vertical, 4)
                
                if type == "exam" {
                    Button {
                        showingExamPicker = true
                    } label: {
                        HStack {
                            Text(NSLocalizedString("Related Exam", comment: "Form field"))
                            Spacer()
                            Text(relatedExam?.name ?? NSLocalizedString("None", comment: "No selection"))
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
            
            Section(header: Text(NSLocalizedString("Notes", comment: "Form field"))) {
                TextEditor(text: $notes)
                    .frame(minHeight: 100)
            }
            
            Section {
                Button {
                    saveEvent()
                } label: {
                    Text(NSLocalizedString("Save", comment: "Save button"))
                        .frame(maxWidth: .infinity)
                        .foregroundColor(.white)
                }
                .listRowBackground(Color.blue)
                .disabled(title.isEmpty)
            }
        }
        .onAppear {
            // Load related exam if applicable
            if let event = event, let examID = event.examID {
                let exams = Exam.getAllExams(context: viewContext)
                relatedExam = exams.first { $0.id == examID }
            }
        }
        .sheet(isPresented: $showingExamPicker) {
            ExamPickerView { exam in
                relatedExam = exam
                showingExamPicker = false
            }
        }
    }
    
    private func saveEvent() {
        let savedEvent = Event(
            id: event?.id ?? UUID(),
            title: title,
            startDate: startDate,
            endDate: allDay ? calendar.date(bySettingHour: 23, minute: 59, second: 59, of: startDate)! : endDate,
            type: type,
            location: location,
            notes: notes,
            allDay: allDay,
            color: color,
            examID: relatedExam?.id
        )
        
        savedEvent.save(in: viewContext)
        onSave(savedEvent)
        dismiss()
    }
    
    private var calendar: Calendar {
        return Calendar.current
    }
}

struct ExamPickerView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss
    
    var onSelect: (Exam) -> Void
    @State private var exams: [Exam] = []
    
    var body: some View {
        NavigationView {
            List(exams) { exam in
                HStack {
                    VStack(alignment: .leading) {
                        Text(exam.name)
                            .font(.headline)
                        
                        Text("\(exam.credits) CFU")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    StatusBadge(status: exam.status)
                }
                .contentShape(Rectangle())
                .onTapGesture {
                    onSelect(exam)
                }
            }
            .navigationTitle(NSLocalizedString("Select Exam", comment: "Navigation title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(NSLocalizedString("Cancel", comment: "Cancel button")) {
                        dismiss()
                    }
                }
            }
            .onAppear {
                loadExams()
            }
        }
    }
    
    private func loadExams() {
        exams = Exam.getAllExams(context: viewContext)
    }
}

struct EventFormView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            EventFormView(date: Date()) { _ in }
        }
    }
}
