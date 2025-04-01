import CoreData

struct PersistenceController {
    static let shared = PersistenceController()
    
    let container: NSPersistentContainer
    
    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "CoreDataModel")
        
        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }
        
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Error loading Core Data stores: \(error.localizedDescription)")
            }
        }
        
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        container.viewContext.automaticallyMergesChangesFromParent = true
        
        // Set up default settings if first launch
        setupDefaultSettingsIfNeeded()
    }
    
    private func setupDefaultSettingsIfNeeded() {
        let context = container.viewContext
        
        // Check if settings exist
        let fetchRequest: NSFetchRequest<SettingEntity> = SettingEntity.fetchRequest()
        let count = try? context.count(for: fetchRequest)
        
        if count == 0 {
            // Create default settings
            let defaultSettings = [
                ("degree_name", "Computer Science"),
                ("total_credits", "180"),
                ("max_grade", "30"),
                ("pass_threshold", "18"),
                ("target_average", "100")
            ]
            
            for (key, value) in defaultSettings {
                let setting = SettingEntity(context: context)
                setting.key = key
                setting.value = value
            }
            
            try? context.save()
        }
    }
    
    // Helper method to get a setting
    func getSetting(key: String, defaultValue: String) -> String {
        let context = container.viewContext
        let fetchRequest: NSFetchRequest<SettingEntity> = SettingEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "key == %@", key)
        
        do {
            let results = try context.fetch(fetchRequest)
            if let setting = results.first, let value = setting.value {
                return value
            }
        } catch {
            print("Error fetching setting: \(error)")
        }
        
        return defaultValue
    }
    
    // Helper method to update a setting
    func updateSetting(key: String, value: String) {
        let context = container.viewContext
        let fetchRequest: NSFetchRequest<SettingEntity> = SettingEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "key == %@", key)
        
        do {
            let results = try context.fetch(fetchRequest)
            if let setting = results.first {
                setting.value = value
            } else {
                let setting = SettingEntity(context: context)
                setting.key = key
                setting.value = value
            }
            
            try context.save()
        } catch {
            print("Error updating setting: \(error)")
        }
    }
}
