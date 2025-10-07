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
- **Installazione automatica** per PC client Linux Mint
- **App non chiudibile**: riavvio automatico dopo 100ms

## Tech Stack
- **Linguaggio**: Python 3.12
- **Librerie**: Solo librerie standard (pathlib, subprocess, re, os, sys, time)
- **Dipendenze**: Nessuna dipendenza esterna
- **Cache server**: Script bash con fd (find alternative) su srv03
- **Installazione**: Script bash automatico per Linux Mint
- **Supervisione**: Wrapper script per riavvio automatico

## Struttura progetto
```
apri_disegno/
├── apri_disegno.py              # File principale
├── apri_disegno_loop.sh         # Wrapper riavvio automatico (generato)
├── update_pdf_cache.sh          # Script cache server srv03
├── install.sh                   # Script installazione automatica Linux Mint
├── etc/
│   ├── fstab.add.txt            # Righe da aggiungere a fstab
│   └── samba/
│       └── credenziali          # Credenziali CIFS (chmod 600)
├── README.md                    # Documentazione
├── .gitignore                   # Gitignore standard Python
├── .cache_timestamp             # Cache timestamp (escluso da git)
└── .git/                        # Repository Git
```

## Architettura
- Singolo file Python con funzioni modulari
- Gestione errori robusta
- Supporto multi-piattaforma
- Pattern di ricerca con regex per cartelle valide
- Cache globale con controllo temporale automatico per DB_DISEGNI
- Cache file testuale per elaborati_tecnici (generata da script server)
- **Installazione automatica** con mount CIFS e icone desktop
- **Supervisione processo**: wrapper script per riavvio automatico

## Performance
- Cache cartelle valide DB_DISEGNI (40 cartelle) caricata solo al primo accesso
- Ricaricamento automatico ogni 8 ore
- Timestamp persistente su file per mantenere stato tra riavvii
- Cache elaborati_tecnici aggiornata automaticamente su server srv03
- Riavvio app in 100ms se chiusa dall'utente

## Logica di ricerca
1. **Prima ricerca**: DB_DISEGNI con cache intelligente
2. **Seconda ricerca**: Solo se prima ricerca = 0 risultati, cerca in elaborati_tecnici via cache file
3. **Visualizzazione**: Colori differenziati per origine (verde/giallo)

## Installazione client Linux Mint
- **Repository**: https://github.com/rylos/apri_disegno.git
- **Percorso**: /home/prod/apri_disegno/
- **Mount points**: /mnt/srv01/DB_DISEGNI, /mnt/srv03/elaborati_tecnici
- **Credenziali**: /etc/samba/credenziali (chmod 600)
- **Icone desktop**: Apri Disegno, MES Qualitas, Elaborati Tecnici (in /home/prod/Scrivania)
- **Avvio automatico**: App si avvia all'accensione PC
- **App persistente**: Riavvio automatico se chiusa (100ms)
- **Aggiornamenti**: Git pull automatico alle 6:00 (cron + anacron)
- **Esecuzione**: sudo ./install.sh