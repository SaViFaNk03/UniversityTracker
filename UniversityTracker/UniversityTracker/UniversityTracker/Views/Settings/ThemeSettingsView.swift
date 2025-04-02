import SwiftUI

struct ThemeSettingsView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.colorScheme) var colorScheme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Tema")
                .font(.title)
                .bold()
                .foregroundColor(themeManager.colors.text)
            
            VStack(alignment: .leading, spacing: 15) {
                // Opzione per seguire il tema di sistema
                Toggle(isOn: $themeManager.followSystemTheme.animation(.easeInOut(duration: 0.3))) {
                    HStack {
                        Image(systemName: "iphone")
                            .foregroundColor(themeManager.colors.primary)
                            .imageScale(.large)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Usa tema di sistema")
                                .foregroundColor(themeManager.colors.text)
                            
                            Text("Segui automaticamente le impostazioni iOS")
                                .font(.caption)
                                .foregroundColor(themeManager.colors.secondaryText)
                        }
                    }
                }
                .toggleStyle(SwitchToggleStyle(tint: themeManager.colors.accent))
                .onChange(of: themeManager.followSystemTheme) { newValue in
                    if newValue {
                        // Se attivato, aggiorna immediatamente in base al tema di sistema
                        themeManager.updateWithSystemTheme(isDark: colorScheme == .dark)
                    }
                }
                
                // Divisore con descrizione contestuale
                HStack {
                    Divider()
                        .background(themeManager.colors.divider)
                    
                    if themeManager.followSystemTheme {
                        Text("Tema del sistema: \(colorScheme == .dark ? "Scuro" : "Chiaro")")
                            .font(.caption)
                            .foregroundColor(themeManager.colors.secondaryText)
                    } else {
                        Text("Selezione manuale")
                            .font(.caption)
                            .foregroundColor(themeManager.colors.secondaryText)
                    }
                    
                    Divider()
                        .background(themeManager.colors.divider)
                }
                .padding(.vertical, 8)
                
                // Toggle per modalità chiara/scura (disabilitato se segue il sistema)
                Toggle(isOn: $themeManager.isDarkMode.animation(.easeInOut(duration: 0.3))) {
                    HStack {
                        Image(systemName: themeManager.isDarkMode ? "moon.fill" : "sun.max.fill")
                            .foregroundColor(themeManager.isDarkMode ? .yellow : .orange)
                            .imageScale(.large)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(themeManager.isDarkMode ? "Modalità scura" : "Modalità chiara")
                                .foregroundColor(themeManager.colors.text)
                            
                            if themeManager.followSystemTheme {
                                Text("Gestito automaticamente dal sistema")
                                    .font(.caption)
                                    .foregroundColor(themeManager.colors.secondaryText)
                            }
                        }
                    }
                }
                .toggleStyle(SwitchToggleStyle(tint: themeManager.colors.accent))
                .disabled(themeManager.followSystemTheme)
                .opacity(themeManager.followSystemTheme ? 0.6 : 1.0)
                
                Divider()
                    .background(themeManager.colors.divider)
                
                ThemePreviewCard(themeManager: themeManager)
            }
            .padding()
            .background(themeManager.colors.cardBackground)
            .cornerRadius(12)
            .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
            
            Spacer()
        }
        .padding()
        .background(themeManager.colors.background)
        .animation(.easeInOut(duration: 0.3), value: themeManager.isDarkMode)
        .onChange(of: colorScheme) { newValue in
            // Quando il tema di sistema cambia, aggiorna il ThemeManager
            themeManager.updateWithSystemTheme(isDark: newValue == .dark)
        }
        .onAppear {
            // All'apertura della vista, sincronizza con il tema di sistema corrente
            themeManager.updateWithSystemTheme(isDark: colorScheme == .dark)
        }
    }
}

// Card preview per il tema selezionato
struct ThemePreviewCard: View {
    @ObservedObject var themeManager: ThemeManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Anteprima del tema")
                .font(.headline)
                .foregroundColor(themeManager.colors.text)
            
            VStack(spacing: 10) {
                // Esempio di testo
                HStack {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(themeManager.colors.primary)
                        .frame(width: 40, height: 40)
                        .overlay(
                            Image(systemName: "graduationcap.fill")
                                .foregroundColor(themeManager.colors.buttonText)
                        )
                    
                    VStack(alignment: .leading) {
                        Text("Esempio di titolo")
                            .font(.headline)
                            .foregroundColor(themeManager.colors.text)
                        
                        Text("Esempio di sottotitolo")
                            .font(.subheadline)
                            .foregroundColor(themeManager.colors.secondaryText)
                    }
                    
                    Spacer()
                    
                    Circle()
                        .fill(themeManager.colors.statusPassed)
                        .frame(width: 15, height: 15)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 12)
                .background(themeManager.colors.secondaryBackground)
                .cornerRadius(8)
                
                // Esempio di bottoni
                HStack(spacing: 12) {
                    Button(action: {}) {
                        Text("Primario")
                            .foregroundColor(themeManager.colors.buttonText)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(themeManager.colors.primary)
                            .cornerRadius(8)
                    }
                    
                    Button(action: {}) {
                        Text("Secondario")
                            .foregroundColor(themeManager.colors.primary)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(themeManager.colors.background)
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(themeManager.colors.primary, lineWidth: 1)
                            )
                    }
                }
                
                // Esempio di campo di input
                HStack {
                    TextField("Inserisci testo", text: .constant(""))
                        .padding(10)
                        .background(themeManager.colors.inputBackground)
                        .cornerRadius(8)
                        .foregroundColor(themeManager.colors.inputText)
                    
                    Button(action: {}) {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(themeManager.colors.buttonText)
                            .padding(10)
                            .background(themeManager.colors.primary)
                            .cornerRadius(8)
                    }
                }
            }
            .padding()
            .background(themeManager.colors.background)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(themeManager.colors.border, lineWidth: 1)
            )
        }
        .animation(.easeInOut(duration: 0.3), value: themeManager.isDarkMode)
    }
}

// Anteprima per la modalità di sviluppo
struct ThemeSettingsView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            ThemeSettingsView()
                .environmentObject(ThemeManager())
            
            ThemeSettingsView()
                .environmentObject({
                    let manager = ThemeManager()
                    manager.isDarkMode = true
                    return manager
                }())
        }
    }
}