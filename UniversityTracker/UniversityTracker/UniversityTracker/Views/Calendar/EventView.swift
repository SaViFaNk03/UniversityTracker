import SwiftUI

struct EventView: View {
    var event: Event
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Title and type
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Circle()
                            .fill(event.color)
                            .frame(width: 10, height: 10)
                        
                        Text(event.type.capitalized)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    Text(event.title)
                        .font(.title)
                        .fontWeight(.bold)
                        .fixedSize(horizontal: false, vertical: true)
                }
                
                Divider()
                
                // Date & time
                VStack(alignment: .leading, spacing: 8) {
                    Label {
                        Text(DateFormatter.monthDayYear.string(from: event.startDate))
                            .font(.headline)
                    } icon: {
                        Image(systemName: "calendar")
                    }
                    
                    if event.allDay {
                        Label {
                            Text(NSLocalizedString("All Day", comment: "Event detail"))
                                .font(.subheadline)
                        } icon: {
                            Image(systemName: "clock")
                        }
                    } else {
                        Label {
                            Text("\(DateFormatter.time.string(from: event.startDate)) - \(DateFormatter.time.string(from: event.endDate))")
                                .font(.subheadline)
                        } icon: {
                            Image(systemName: "clock")
                        }
                    }
                }
                
                // Location if available
                if let location = event.location, !location.isEmpty {
                    Divider()
                    
                    Label {
                        Text(location)
                            .font(.headline)
                    } icon: {
                        Image(systemName: "mappin.and.ellipse")
                    }
                }
                
                // Notes if available
                if let notes = event.notes, !notes.isEmpty {
                    Divider()
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Label {
                            Text(NSLocalizedString("Notes", comment: "Event detail"))
                                .font(.headline)
                        } icon: {
                            Image(systemName: "note.text")
                        }
                        
                        Text(notes)
                            .font(.body)
                            .padding()
                            .background(Color.secondaryBackground)
                            .cornerRadius(8)
                    }
                }
                
                // Related exam if applicable
                if let examID = event.examID {
                    Divider()
                    
                    Label {
                        Text(NSLocalizedString("Related Exam", comment: "Event detail"))
                            .font(.headline)
                    } icon: {
                        Image(systemName: "doc.text.magnifyingglass")
                    }
                    
                    // TODO: Implement relation to exam
                }
                
                Spacer()
            }
            .padding()
        }
        .navigationTitle(NSLocalizedString("Event Details", comment: "Navigation title"))
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct EventView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            EventView(
                event: Event(
                    title: "Advanced Algorithms Exam",
                    startDate: Date(),
                    endDate: Date().addingTimeInterval(7200),
                    type: "exam",
                    location: "Room B1.12, CS Department",
                    notes: "Bring calculator and one A4 cheat sheet with formulas. No phones allowed.",
                    allDay: false,
                    color: .blue
                )
            )
        }
    }
}
