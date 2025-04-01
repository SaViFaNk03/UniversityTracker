import Foundation
import CoreData
import SwiftUI

struct AcademicSession: Identifiable {
    var id: UUID
    var title: String
    var startDate: Date
    var endDate: Date
    var color: Color
    var notes: String?
    
    init(id: UUID = UUID(), title: String, startDate: Date, endDate: Date, color: Color, notes: String? = nil) {
        self.id = id
        self.title = title
        self.startDate = startDate
        self.endDate = endDate
        self.color = color
        self.notes = notes
    }
    
    init?(entity: EventEntity) {
        guard entity.type == "academic_session" else { return nil }
        
        self.id = entity.id ?? UUID()
        self.title = entity.title ?? ""
        self.startDate = entity.startDate ?? Date()
        self.endDate = entity.endDate ?? Date()
        self.notes = entity.notes
        
        if let colorString = entity.color {
            self.color = Color(hex: colorString) ?? .blue
        } else {
            self.color = .blue
        }
    }
    
    func save(in context: NSManagedObjectContext) {
        let fetchRequest: NSFetchRequest<EventEntity> = EventEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@ AND type == %@", id as CVarArg, "academic_session")
        
        do {
            let results = try context.fetch(fetchRequest)
            let session: EventEntity
            
            if let existingSession = results.first {
                session = existingSession
            } else {
                session = EventEntity(context: context)
                session.id = id
                session.type = "academic_session"
            }
            
            session.title = title
            session.startDate = startDate
            session.endDate = endDate
            session.color = color.toHex()
            session.notes = notes
            session.allDay = true
            
            try context.save()
        } catch {
            print("Error saving academic session: \(error)")
        }
    }
    
    static func getSessions(context: NSManagedObjectContext) -> [AcademicSession] {
        let fetchRequest: NSFetchRequest<EventEntity> = EventEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "type == %@", "academic_session")
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.compactMap { AcademicSession(entity: $0) }
        } catch {
            print("Error fetching academic sessions: \(error)")
            return []
        }
    }
    
    static func delete(session: AcademicSession, context: NSManagedObjectContext) {
        let fetchRequest: NSFetchRequest<EventEntity> = EventEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@ AND type == %@", session.id as CVarArg, "academic_session")
        
        do {
            let results = try context.fetch(fetchRequest)
            if let sessionEntity = results.first {
                context.delete(sessionEntity)
                try context.save()
            }
        } catch {
            print("Error deleting academic session: \(error)")
        }
    }
}
