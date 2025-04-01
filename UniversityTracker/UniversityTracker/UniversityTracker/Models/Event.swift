import Foundation
import CoreData
import SwiftUI

struct Event: Identifiable {
    var id: UUID
    var title: String
    var startDate: Date
    var endDate: Date
    var type: String // "exam", "study", "personal", etc.
    var location: String?
    var notes: String?
    var allDay: Bool
    var color: Color
    var examID: UUID? // Optional reference to an exam
    
    init(id: UUID = UUID(), title: String, startDate: Date, endDate: Date, type: String, location: String? = nil, notes: String? = nil, allDay: Bool = false, color: Color = .blue, examID: UUID? = nil) {
        self.id = id
        self.title = title
        self.startDate = startDate
        self.endDate = endDate
        self.type = type
        self.location = location
        self.notes = notes
        self.allDay = allDay
        self.color = color
        self.examID = examID
    }
    
    init(entity: EventEntity) {
        self.id = entity.id ?? UUID()
        self.title = entity.title ?? ""
        self.startDate = entity.startDate ?? Date()
        self.endDate = entity.endDate ?? Date()
        self.type = entity.type ?? "personal"
        self.location = entity.location
        self.notes = entity.notes
        self.allDay = entity.allDay
        self.examID = entity.examID
        
        if let colorString = entity.color {
            self.color = Color(hex: colorString) ?? .blue
        } else {
            self.color = .blue
        }
    }
    
    func save(in context: NSManagedObjectContext) {
        let fetchRequest: NSFetchRequest<EventEntity> = EventEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@", id as CVarArg)
        
        do {
            let results = try context.fetch(fetchRequest)
            let event: EventEntity
            
            if let existingEvent = results.first {
                event = existingEvent
            } else {
                event = EventEntity(context: context)
                event.id = id
            }
            
            event.title = title
            event.startDate = startDate
            event.endDate = endDate
            event.type = type
            event.location = location
            event.notes = notes
            event.allDay = allDay
            event.color = color.toHex()
            event.examID = examID
            
            try context.save()
        } catch {
            print("Error saving event: \(error)")
        }
    }
    
    static func getEvents(forDate date: Date? = nil, context: NSManagedObjectContext) -> [Event] {
        let fetchRequest: NSFetchRequest<EventEntity> = EventEntity.fetchRequest()
        
        if let date = date {
            let calendar = Calendar.current
            let startOfDay = calendar.startOfDay(for: date)
            let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!
            
            fetchRequest.predicate = NSPredicate(
                format: "(startDate >= %@ AND startDate < %@) OR (endDate >= %@ AND endDate < %@) OR (startDate <= %@ AND endDate >= %@)",
                startOfDay as NSDate, endOfDay as NSDate,
                startOfDay as NSDate, endOfDay as NSDate,
                startOfDay as NSDate, endOfDay as NSDate
            )
        }
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.map { Event(entity: $0) }
        } catch {
            print("Error fetching events: \(error)")
            return []
        }
    }
    
    static func getEvents(forMonth month: Int, year: Int, context: NSManagedObjectContext) -> [Event] {
        let calendar = Calendar.current
        
        var dateComponents = DateComponents()
        dateComponents.year = year
        dateComponents.month = month
        dateComponents.day = 1
        
        guard let startDate = calendar.date(from: dateComponents) else {
            return []
        }
        
        dateComponents.month = month + 1
        guard let endDate = calendar.date(from: dateComponents) else {
            return []
        }
        
        let fetchRequest: NSFetchRequest<EventEntity> = EventEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(
            format: "(startDate >= %@ AND startDate < %@) OR (endDate >= %@ AND endDate < %@) OR (startDate <= %@ AND endDate >= %@)",
            startDate as NSDate, endDate as NSDate,
            startDate as NSDate, endDate as NSDate,
            startDate as NSDate, endDate as NSDate
        )
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.map { Event(entity: $0) }
        } catch {
            print("Error fetching events: \(error)")
            return []
        }
    }
    
    static func delete(event: Event, context: NSManagedObjectContext) {
        let fetchRequest: NSFetchRequest<EventEntity> = EventEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@", event.id as CVarArg)
        
        do {
            let results = try context.fetch(fetchRequest)
            if let eventEntity = results.first {
                context.delete(eventEntity)
                try context.save()
            }
        } catch {
            print("Error deleting event: \(error)")
        }
    }
}
