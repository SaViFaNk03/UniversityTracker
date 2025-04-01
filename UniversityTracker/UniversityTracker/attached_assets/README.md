# University Career Manager

Un'applicazione desktop per la gestione completa della carriera universitaria. Questa applicazione ti permette di tenere traccia dei tuoi esami (passati e non passati), dei CFU (totali e ottenuti finora), della media complessiva, della media ponderata e ti aiuta a pianificare gli esami futuri in base ai tuoi obiettivi.

## Funzionalità

- **Dashboard**: visualizza un riepilogo della tua carriera universitaria, inclusi i crediti guadagnati, la media e i progressi complessivi.
- **Gestione Esami**: aggiungi, modifica ed elimina gli esami, con dettagli su voti, crediti, date e note.
- **Analisi**: visualizza statistiche dettagliate sulla tua carriera, comprese le medie semplice e ponderata, entrambe convertite anche nella scala 110.
- **Calcolo Obiettivi Intelligente e Personalizzabile**: scopri quali voti devi ottenere nei prossimi esami per raggiungere la media desiderata, con l'algoritmo che considera gli esami con più CFU come più difficili (suggerendo voti più alti per gli esami facili e più bassi per quelli difficili). Puoi anche modificare manualmente i voti target di alcuni esami, con ricalcolo automatico degli altri.
- **Impostazioni**: personalizza il sistema di valutazione, i crediti richiesti per la laurea e altre preferenze.
- **Esportazione/Importazione**: salva e carica i tuoi dati per il backup o il trasferimento.

## Requisiti

- Python 3.6+
- PyQt5
- Matplotlib

## Installazione

1. Assicurati di avere Python installato sul tuo sistema.
2. Installa le dipendenze richieste:

```bash
pip install PyQt5 matplotlib
```

3. Scarica il codice sorgente da questo repository.
4. Esegui l'applicazione:

```bash
python main.py
```

## Utilizzo

### Dashboard

La dashboard mostra una panoramica della tua carriera universitaria con statistiche chiave:
- Crediti ottenuti e totali necessari per la laurea
- Media semplice e ponderata (sia in scala originale che convertita in 110)
- Grafico a torta della distribuzione degli esami (passati, falliti, pianificati)
- Grafico a barre della distribuzione dei voti

### Gestione Esami

Questa sezione ti permette di gestire tutti i tuoi esami:
- Aggiungi nuovi esami con nome, crediti, stato, voto (se superato), data e note
- Modifica o elimina esami esistenti
- Filtra gli esami per stato (passati, falliti, pianificati)

### Analisi

La sezione analisi offre statistiche approfondite:
- Medie dettagliate (semplice e ponderata)
- Crediti ottenuti e rimanenti
- Grafico dell'andamento dei voti nel tempo
- Calcolo dei voti necessari per raggiungere la media obiettivo
- Algoritmo intelligente che assegna voti target più alti agli esami con meno CFU (presumibilmente più facili) e voti più bassi agli esami con più CFU (presumibilmente più difficili)
- Possibilità di modificare manualmente i voti target per singoli esami, con ricalcolo automatico degli altri voti target per mantenere la media obiettivo

### Impostazioni

Personalizza l'applicazione in base alle tue esigenze:
- Nome del corso di laurea
- Crediti totali richiesti per la laurea
- Sistema di valutazione (voto massimo e soglia di superamento)
- Media obiettivo
- Opzioni di importazione/esportazione dei dati

## Salvataggio dei Dati

L'applicazione salva automaticamente tutti i dati in un database SQLite nella cartella Documenti/UniversityCareerManager. Questo garantisce che i tuoi dati siano al sicuro e persistenti tra le sessioni.

## Contribuzione

Sei libero di contribuire a questo progetto inviando pull request o segnalando problemi tramite le issues.

## Licenza

Questo progetto è rilasciato sotto licenza MIT. Sei libero di utilizzarlo e modificarlo come desideri.