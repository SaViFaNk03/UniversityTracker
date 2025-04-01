import SwiftUI

struct ExamsListView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @State private var exams: [Exam] = []
    @State private var filteredExams: [Exam] = []
    @State private var selectedStatus: ExamStatus? = nil
    @State private var showingAddExam = false
    @State private var examToEdit: Exam? = nil
    @State private var showingDeleteAlert = false
    @State private var examToDelete: Exam? = nil
    
    var body: some View {
        NavigationView {
            VStack {
                // Filter picker
                Picker(NSLocalizedString("Filter", comment: "Exam filter"), selection: $selectedStatus) {
                    Text(NSLocalizedString("All Exams", comment: "Filter option"))
                        .tag(nil as ExamStatus?)
                    
                    ForEach(ExamStatus.allCases) { status in
                        Text(status.localizedName)
                            .tag(status as ExamStatus?)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)
                .padding(.top, 8)
                
                // Exams table
                List {
                    ForEach(filteredExams) { exam in
                        ExamRow(exam: exam)
                            .swipeActions(edge: .trailing) {
                                Button(role: .destructive) {
                                    examToDelete = exam
                                    showingDeleteAlert = true
                                } label: {
                                    Label(NSLocalizedString("Delete", comment: "Delete exam"), systemImage: "trash")
                                }
                                
                                Button {
                                    examToEdit = exam
                                } label: {
                                    Label(NSLocalizedString("Edit", comment: "Edit exam"), systemImage: "pencil")
                                }
                                .tint(.blue)
                            }
                            .swipeActions(edge: .leading) {
                                if exam.status == .planned {
                                    Button {
                                        // TODO: Add implementation for scheduling exam in calendar
                                        scheduleExam(exam)
                                    } label: {
                                        Label(NSLocalizedString("Schedule", comment: "Schedule exam"), systemImage: "calendar.badge.plus")
                                    }
                                    .tint(.green)
                                }
                            }
                    }
                }
            }
            .navigationTitle(NSLocalizedString("Exam Management", comment: "Exams view title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showingAddExam = true
                    } label: {
                        Label(NSLocalizedString("Add Exam", comment: "Add exam button"), systemImage: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddExam) {
                NavigationView {
                    ExamFormView(exam: nil) { _ in
                        loadExams()
                        showingAddExam = false
                    }
                    .navigationTitle(NSLocalizedString("Add Exam", comment: "Add exam form title"))
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button(NSLocalizedString("Cancel", comment: "Cancel button")) {
                                showingAddExam = false
                            }
                        }
                    }
                }
            }
            .sheet(item: $examToEdit) { exam in
                NavigationView {
                    ExamFormView(exam: exam) { _ in
                        loadExams()
                        examToEdit = nil
                    }
                    .navigationTitle(NSLocalizedString("Edit Exam", comment: "Edit exam form title"))
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button(NSLocalizedString("Cancel", comment: "Cancel button")) {
                                examToEdit = nil
                            }
                        }
                    }
                }
            }
            .alert(NSLocalizedString("Delete Confirmation", comment: "Delete confirmation title"), isPresented: $showingDeleteAlert) {
                Button(NSLocalizedString("Cancel", comment: "Cancel button"), role: .cancel) { }
                Button(NSLocalizedString("Delete", comment: "Delete button"), role: .destructive) {
                    if let exam = examToDelete {
                        deleteExam(exam)
                    }
                }
            } message: {
                Text(NSLocalizedString("Are you sure you want to delete this exam? This action cannot be undone.", comment: "Delete warning"))
            }
            .onAppear {
                loadExams()
            }
            .onChange(of: selectedStatus) { oldValue, newValue in
                filterExams()
            }
        }
    }
    
    private func loadExams() {
        exams = Exam.getAllExams(context: viewContext)
        filterExams()
    }
    
    private func filterExams() {
        if let status = selectedStatus {
            filteredExams = exams.filter { $0.status == status }
        } else {
            filteredExams = exams
        }
    }
    
    private func deleteExam(_ exam: Exam) {
        Exam.delete(exam: exam, context: viewContext)
        loadExams()
        examToDelete = nil
    }
    
    private func scheduleExam(_ exam: Exam) {
        // Create a calendar event for this exam
        let event = Event(
            title: exam.name,
            startDate: exam.date ?? Date(),
            endDate: (exam.date ?? Date()).addingTimeInterval(3600 * 2), // 2 hours by default
            type: "exam",
            location: "", // Default empty location
            allDay: false,
            color: .blue,
            examID: exam.id
        )
        
        event.save(in: viewContext)
    }
}

struct ExamRow: View {
    var exam: Exam
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(exam.name)
                .font(.headline)
            
            HStack {
                Label("\(exam.credits) CFU", systemImage: "creditcard")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                if let grade = exam.grade, exam.status == .passed {
                    Label("\(Int(grade))", systemImage: "star.fill")
                        .font(.caption)
                        .foregroundColor(.yellow)
                }
                
                StatusBadge(status: exam.status)
                
                if let date = exam.date {
                    Label(DateFormatter.shortDate.string(from: date), systemImage: "calendar")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

struct StatusBadge: View {
    var status: ExamStatus
    
    var body: some View {
        Text(status.localizedName)
            .font(.caption)
            .padding(.horizontal, 8)
            .padding(.vertical, 2)
            .background(backgroundColor)
            .foregroundColor(.white)
            .cornerRadius(4)
    }
    
    var backgroundColor: Color {
        switch status {
        case .passed:
            return .statusPassed
        case .failed:
            return .statusFailed
        case .planned:
            return .statusPlanned
        }
    }
}

struct ExamsListView_Previews: PreviewProvider {
    static var previews: some View {
        ExamsListView()
            .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
    }
}
