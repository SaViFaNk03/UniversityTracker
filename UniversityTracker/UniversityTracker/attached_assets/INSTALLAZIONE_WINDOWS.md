# Guida all'Installazione per Windows

## Requisiti di Sistema
- Windows 10 o successivo
- Python 3.6 o successivo

## Metodo 1: Installazione Rapida (Consigliato)

1. **Scarica tutti i file** di questo progetto sul tuo computer
2. **Fai doppio clic** sul file `start_app.bat`
3. L'applicazione verificherà automaticamente la presenza di Python, installerà le dipendenze necessarie e avvierà il programma

## Metodo 2: Installazione Manuale

### Passo 1: Installa Python
1. Scarica l'ultima versione di Python da [python.org](https://www.python.org/downloads/windows/)
2. Durante l'installazione, assicurati di selezionare l'opzione **"Add Python to PATH"**
3. Completa l'installazione

### Passo 2: Installa le Dipendenze
1. Apri il **Prompt dei Comandi** (cerca "cmd" nel menu Start)
2. Naviga fino alla cartella dove hai scaricato i file del progetto:
   ```
   cd percorso\alla\cartella\university-career-manager
   ```
3. Installa le dipendenze richieste:
   ```
   pip install -r requirements-app.txt
   ```

### Passo 3: Avvia l'Applicazione
1. Dalla stessa finestra del Prompt dei Comandi, esegui:
   ```
   python main.py
   ```
2. L'applicazione University Career Manager si avvierà

## Risoluzione dei Problemi

### Python non è riconosciuto come comando
- Assicurati di aver selezionato l'opzione "Add Python to PATH" durante l'installazione
- Riavvia il computer
- Se il problema persiste, aggiungi manualmente Python al PATH di sistema

### Errori durante l'installazione delle dipendenze
- Assicurati di avere accesso a Internet
- Prova ad aggiornare pip:
  ```
  python -m pip install --upgrade pip
  ```
- Poi riprova a installare le dipendenze

### L'interfaccia grafica non si avvia
- Verifica di aver installato PyQt5 correttamente:
  ```
  pip show PyQt5
  ```
- Se necessario, reinstalla PyQt5:
  ```
  pip uninstall PyQt5
  pip install PyQt5
  ```

## Informazioni sul Salvataggio dei Dati

Tutti i dati dell'applicazione vengono salvati nella cartella:
```
C:\Users\[TuoNomeUtente]\Documents\UniversityCareerManager\
```

Per eseguire un backup dei tuoi dati, copia il file `university_career.db` da questa cartella.

## Aiuto e Supporto

Per assistenza, contatta il supporto all'indirizzo email: [inserire email di supporto]