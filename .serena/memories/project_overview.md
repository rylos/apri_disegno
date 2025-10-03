# Progetto apri_disegno

## Scopo
Programma Python per ricerca e apertura di disegni PDF da percorso di rete aziendale (srv01/DB_DISEGNI).

## Funzionalità principali
- Ricerca file PDF per codice disegno
- Supporto cross-platform (Windows/Linux)
- Apertura automatica con programma predefinito
- Interfaccia a riga di comando interattiva

## Tech Stack
- **Linguaggio**: Python 3.12
- **Librerie**: Solo librerie standard (pathlib, subprocess, re, os, sys)
- **Dipendenze**: Nessuna dipendenza esterna

## Struttura progetto
```
apri_disegno/
├── apri_disegno.py    # File principale
├── .gitignore         # Gitignore standard Python
└── .git/              # Repository Git
```

## Architettura
- Singolo file Python con funzioni modulari
- Gestione errori robusta
- Supporto multi-piattaforma
- Pattern di ricerca con regex per cartelle valide