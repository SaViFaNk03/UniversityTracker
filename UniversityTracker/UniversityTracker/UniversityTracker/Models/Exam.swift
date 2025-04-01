import Foundation
import CoreData

enum ExamStatus: String, CaseIterable, Identifiable {
    case passed = "passed"
    case failed = "failed"
    case planned = "planned"
    
    var id: String { self.rawValue }
    
    var localizedName: String {
        switch self {
        case .passed:
            return NSLocalizedString("Passed", comment: "Exam status passed")
        case .failed:
            return NSLocalizedString("Failed", comment: "Exam status failed")
        case .planned:
            return NSLocalizedString("Planned", comment: "Exam status planned")
        }
    }
}

struct Exam: Identifiable {
    var id: UUID
    var name: String
    var credits: Int
    var status: ExamStatus
    var grade: Double?
    var date: Date?
    var notes: String?
    
    init(entity: ExamEntity) {
        self.id = entity.id ?? UUID()
        self.name = entity.name ?? ""
        self.credits = Int(entity.credits)
        self.status = ExamStatus(rawValue: entity.status ?? "planned") ?? .planned
        self.grade = entity.grade > 0 ? entity.grade : nil
        self.date = entity.date
        self.notes = entity.notes
    }
    
    init(id: UUID = UUID(), name: String, credits: Int, status: ExamStatus, grade: Double? = nil, date: Date? = nil, notes: String? = nil) {
        self.id = id
        self.name = name
        self.credits = credits
        self.status = status
        self.grade = grade
        self.date = date
        self.notes = notes
    }
    
    static func getAllExams(context: NSManagedObjectContext) -> [Exam] {
        let fetchRequest: NSFetchRequest<ExamEntity> = ExamEntity.fetchRequest()
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.map { Exam(entity: $0) }
        } catch {
            print("Error fetching exams: \(error)")
            return []
        }
    }
    
    static func getExams(withStatus status: ExamStatus? = nil, context: NSManagedObjectContext) -> [Exam] {
        let fetchRequest: NSFetchRequest<ExamEntity> = ExamEntity.fetchRequest()
        
        if let status = status {
            fetchRequest.predicate = NSPredicate(format: "status == %@", status.rawValue)
        }
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.map { Exam(entity: $0) }
        } catch {
            print("Error fetching exams: \(error)")
            return []
        }
    }
    
    func save(in context: NSManagedObjectContext) {
        let fetchRequest: NSFetchRequest<ExamEntity> = ExamEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@", id as CVarArg)
        
        do {
            let results = try context.fetch(fetchRequest)
            let exam: ExamEntity
            
            if let existingExam = results.first {
                exam = existingExam
            } else {
                exam = ExamEntity(context: context)
                exam.id = id
            }
            
            exam.name = name
            exam.credits = Int16(credits)
            exam.status = status.rawValue
            exam.grade = grade ?? 0
            exam.date = date
            exam.notes = notes
            
            try context.save()
        } catch {
            print("Error saving exam: \(error)")
        }
    }
    
    static func delete(exam: Exam, context: NSManagedObjectContext) {
        let fetchRequest: NSFetchRequest<ExamEntity> = ExamEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@", exam.id as CVarArg)
        
        do {
            let results = try context.fetch(fetchRequest)
            if let examEntity = results.first {
                context.delete(examEntity)
                try context.save()
            }
        } catch {
            print("Error deleting exam: \(error)")
        }
    }
}
