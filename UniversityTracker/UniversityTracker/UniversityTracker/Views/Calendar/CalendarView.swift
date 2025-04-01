import SwiftUI

struct CalendarView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @State private var currentDate = Date()
    @State private var selectedDate = Date()
    @State private var events: [Event] = []
    @State private var academicSessions: [AcademicSession] = []
    @State private var showingAddEvent = false
    @State private var showingAddSession = false
    
    private let calendar = Calendar.current
    private let daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    private var month: Int {
        return calendar.component(.month, from: currentDate)
    }
    
    private var year: Int {
        return calendar.component(.year, from: currentDate)
    }
    
    private var daysInMonth: Int {
        return calendar.range(of: .day, in: .month, for: currentDate)?.count ?? 0
    }
    
    private var firstDayOfMonth: Date {
        let components = DateComponents(year: year, month: month, day: 1)
        return calendar.date(from: components)!
    }
    
    private var firstWeekdayOfMonth: Int {
        let firstDay = calendar.component(.weekday, from: firstDayOfMonth)
        // Adjust for Monday as first day (1) instead of Sunday (1)
        return (firstDay + 5) % 7 + 1
    }
    
    private var monthString: String {
        return DateFormatter.monthYear.string(from: currentDate)
    }
    
    private var eventsForSelectedDate: [Event] {
        return events.filter { calendar.isDate($0.startDate, inSameDayAs: selectedDate) }
    }
    
    var body: some View {
        NavigationView {
            VStack {
                // Month navigation
                HStack {
                    Button(action: previousMonth) {
                        Image(systemName: "chevron.left")
                            .font(.title2)
                    }
                    
                    Spacer()
                    
                    Text(monthString)
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Spacer()
                    
                    Button(action: nextMonth) {
                        Image(systemName: "chevron.right")
                            .font(.title2)
                    }
                }
                .padding(.horizontal)
                
                // Days of the week header
                HStack {
                    ForEach(daysOfWeek, id: \.self) { day in
                        Text(LocalizedStringKey(day))
                            .font(.caption)
                            .frame(maxWidth: .infinity)
                    }
                }
                .padding(.top, 8)
                
                // Calendar grid
                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 7), spacing: 10) {
                    // Empty cells before the first day of the month
                    ForEach(1..<firstWeekdayOfMonth, id: \.self) { _ in
                        Text("")
                            .frame(height: 40)
                    }
                    
                    // Days of the month
                    ForEach(1...daysInMonth, id: \.self) { day in
                        CalendarDayView(
                            day: day,
                            isSelected: calendar.isDate(dateFor(day), inSameDayAs: selectedDate),
                            isToday: calendar.isDateInToday(dateFor(day)),
                            events: eventsForDay(day),
                            sessions: sessionsForDay(day)
                        )
                        .onTapGesture {
                            selectedDate = dateFor(day)
                        }
                    }
                }
                .padding(.horizontal, 10)
                
                Divider()
                    .padding(.vertical, 8)
                
                // Events for selected day
                VStack(alignment: .leading) {
                    HStack {
                        Text("\(NSLocalizedString("Events for", comment: "Calendar section")) \(DateFormatter.monthDayYear.string(from: selectedDate))")
                            .font(.headline)
                        
                        Spacer()
                        
                        Button(action: {
                            showingAddEvent = true
                        }) {
                            Image(systemName: "plus.circle")
                        }
                    }
                    .padding(.horizontal)
                    
                    if eventsForSelectedDate.isEmpty {
                        Text(NSLocalizedString("No events for this date", comment: "Empty events message"))
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding(.top)
                    } else {
                        List {
                            ForEach(eventsForSelectedDate) { event in
                                EventListItem(event: event)
                            }
                            .onDelete(perform: deleteEvents)
                        }
                    }
                }
                .frame(maxHeight: 250)
            }
            .navigationTitle(NSLocalizedString("Academic Calendar", comment: "Calendar view title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(NSLocalizedString("Today", comment: "Today button")) {
                        currentDate = Date()
                        selectedDate = Date()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button(NSLocalizedString("Add Event", comment: "Add event button")) {
                            showingAddEvent = true
                        }
                        
                        Button(NSLocalizedString("Add Academic Session", comment: "Add session button")) {
                            showingAddSession = true
                        }
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddEvent) {
                NavigationView {
                    EventFormView(date: selectedDate, onSave: { _ in
                        loadEvents()
                    })
                    .navigationTitle(NSLocalizedString("Add Event", comment: "Add event form"))
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button(NSLocalizedString("Cancel", comment: "Cancel button")) {
                                showingAddEvent = false
                            }
                        }
                    }
                }
            }
            .sheet(isPresented: $showingAddSession) {
                NavigationView {
                    AcademicSessionFormView(onSave: { _ in
                        loadEvents()
                    })
                    .navigationTitle(NSLocalizedString("Add Academic Session", comment: "Add session form"))
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button(NSLocalizedString("Cancel", comment: "Cancel button")) {
                                showingAddSession = false
                            }
                        }
                    }
                }
            }
            .onAppear {
                loadEvents()
            }
        }
    }
    
    private func dateFor(_ day: Int) -> Date {
        var components = DateComponents()
        components.year = year
        components.month = month
        components.day = day
        return calendar.date(from: components)!
    }
    
    private func eventsForDay(_ day: Int) -> [Event] {
        let dayDate = dateFor(day)
        return events.filter { calendar.isDate($0.startDate, inSameDayAs: dayDate) }
    }
    
    private func sessionsForDay(_ day: Int) -> [AcademicSession] {
        let dayDate = dateFor(day)
        return academicSessions.filter { session in
            let startDate = session.startDate
            let endDate = session.endDate
            return (startDate...endDate).contains(dayDate)
        }
    }
    
    private func previousMonth() {
        currentDate = calendar.date(byAdding: .month, value: -1, to: currentDate)!
        loadEvents()
    }
    
    private func nextMonth() {
        currentDate = calendar.date(byAdding: .month, value: 1, to: currentDate)!
        loadEvents()
    }
    
    private func loadEvents() {
        events = Event.getEvents(forMonth: month, year: year, context: viewContext)
        academicSessions = AcademicSession.getSessions(context: viewContext)
    }
    
    private func deleteEvents(at offsets: IndexSet) {
        for index in offsets {
            let event = eventsForSelectedDate[index]
            Event.delete(event: event, context: viewContext)
        }
        loadEvents()
    }
}

struct CalendarDayView: View {
    var day: Int
    var isSelected: Bool
    var isToday: Bool
    var events: [Event]
    var sessions: [AcademicSession]
    
    var body: some View {
        ZStack {
            // Session background
            if !sessions.isEmpty {
                RoundedRectangle(cornerRadius: 8)
                    .fill(sessions[0].color.opacity(0.3))
            }
            
            // Selection or today highlight
            if isSelected {
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.blue, lineWidth: 2)
            } else if isToday {
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.green, lineWidth: 2)
            }
            
            VStack(spacing: 4) {
                Text("\(day)")
                    .fontWeight(isToday ? .bold : .regular)
                
                // Event indicators
                if !events.isEmpty {
                    HStack(spacing: 4) {
                        ForEach(0..<min(events.count, 3), id: \.self) { i in
                            Circle()
                                .fill(events[i].color)
                                .frame(width: 6, height: 6)
                        }
                        
                        if events.count > 3 {
                            Text("+\(events.count - 3)")
                                .font(.system(size: 9))
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.top, 2)
                }
            }
            .padding(4)
        }
        .frame(height: 40)
    }
}

struct EventListItem: View {
    var event: Event
    
    var body: some View {
        HStack {
            Rectangle()
                .fill(event.color)
                .frame(width: 4)
                .cornerRadius(2)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(event.title)
                    .font(.headline)
                
                HStack {
                    if event.allDay {
                        Text(NSLocalizedString("All Day", comment: "Calendar event"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    } else {
                        Text("\(DateFormatter.time.string(from: event.startDate)) - \(DateFormatter.time.string(from: event.endDate))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    if let location = event.location, !location.isEmpty {
                        Text("• \(location)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }
}

struct AcademicSessionFormView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss
    
    var onSave: (AcademicSession) -> Void
    
    @State private var title = ""
    @State private var startDate = Date()
    @State private var endDate = Date().addingTimeInterval(60*60*24*30) // Default to 1 month
    @State private var notes = ""
    @State private var color: Color = .blue
    
    var body: some View {
        Form {
            Section(header: Text(NSLocalizedString("Session Details", comment: "Form section"))) {
                TextField(NSLocalizedString("Title", comment: "Form field"), text: $title)
                
                DatePicker(NSLocalizedString("Start Date", comment: "Form field"), selection: $startDate, displayedComponents: .date)
                
                DatePicker(NSLocalizedString("End Date", comment: "Form field"), selection: $endDate, displayedComponents: .date)
                
                VStack(alignment: .leading) {
                    Text(NSLocalizedString("Color", comment: "Form field"))
                    ColorSelectionView(selectedColor: $color)
                }
                .padding(.vertical, 4)
            }
            
            Section(header: Text(NSLocalizedString("Notes", comment: "Form field"))) {
                TextEditor(text: $notes)
                    .frame(minHeight: 100)
            }
            
            Section {
                Button {
                    saveSession()
                } label: {
                    Text(NSLocalizedString("Save", comment: "Save button"))
                        .frame(maxWidth: .infinity)
                        .foregroundColor(.white)
                }
                .listRowBackground(Color.blue)
                .disabled(title.isEmpty)
            }
        }
    }
    
    private func saveSession() {
        let session = AcademicSession(
            title: title,
            startDate: startDate,
            endDate: endDate,
            color: color,
            notes: notes
        )
        
        session.save(in: viewContext)
        onSave(session)
        dismiss()
    }
}

struct CalendarView_Previews: PreviewProvider {
    static var previews: some View {
        CalendarView()
            .environment(\.managedObjectContext, PersistenceController.shared.container.viewContext)
    }
}
