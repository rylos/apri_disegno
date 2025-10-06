# Progetto apri_disegno - Release 1.1

## Scopo
Programma Python per ricerca e apertura di disegni PDF da percorsi di rete aziendale:
- **Primario**: srv01/DB_DISEGNI (ricerca diretta nelle cartelle)
- **Secondario**: srv03/elaborati_tecnici (ricerca tramite cache file)

## Funzionalità principali
- Ricerca file PDF per codice disegno con doppia fonte
- Supporto cross-platform (Windows/Linux)
- Apertura automatica con programma predefinito
- Interfaccia a riga di comando interattiva
- **Cache intelligente** con scadenza 8 ore per DB_DISEGNI
- **Ricerca condizionale**: elaborati_tecnici solo se DB_DISEGNI non trova risultati
- **Colori differenziati**: verde per DB_DISEGNI, giallo per elaborati_tecnici

## Tech Stack
- **Linguaggio**: Python 3.12
- **Librerie**: Solo librerie standard (pathlib, subprocess, re, os, sys, time)
- **Dipendenze**: Nessuna dipendenza esterna
- **Cache server**: Script bash con fd (find alternative) su srv03

## Struttura progetto
```
apri_disegno/
├── apri_disegno.py         # File principale
├── update_pdf_cache.sh     # Script cache server srv03
├── README.md               # Documentazione
├── .gitignore              # Gitignore standard Python
├── .cache_timestamp        # Cache timestamp (escluso da git)
└── .git/                   # Repository Git
```

## Architettura
- Singolo file Python con funzioni modulari
- Gestione errori robusta
- Supporto multi-piattaforma
- Pattern di ricerca con regex per cartelle valide
- Cache globale con controllo temporale automatico per DB_DISEGNI
- Cache file testuale per elaborati_tecnici (generata da script server)

## Performance
- Cache cartelle valide DB_DISEGNI (40 cartelle) caricata solo al primo accesso
- Ricaricamento automatico ogni 8 ore
- Timestamp persistente su file per mantenere stato tra riavvii
- Cache elaborati_tecnici aggiornata automaticamente su server srv03

## Logica di ricerca
1. **Prima ricerca**: DB_DISEGNI con cache intelligente
2. **Seconda ricerca**: Solo se prima ricerca = 0 risultati, cerca in elaborati_tecnici via cache file
3. **Visualizzazione**: Colori differenziati per origine (verde/giallo)