# Progetto apri_disegno - v1.2

## Scopo
Ricerca e apertura rapida di disegni PDF su rete aziendale, con due fonti:
- **Primaria**: `srv01/DB_DISEGNI` (scansione diretta cartelle + cache)
- **Secondaria**: `srv03/elaborati_tecnici` (ricerca su file cache `.pdf_cache.txt`)

Due applicazioni indipendenti che condividono la stessa logica di ricerca:
1. **CLI** — `apri_disegno.py` (zero dipendenze, cross-platform)
2. **Web** — `apri_disegno_web/` (Flask + htmx, deploy Docker)

## Logica di ricerca (identica in CLI e web)
1. Cartelle valide = directory che matchano regex `^[a-zA-Z]\d{3}`, escluse quelle con `OLD`, che contengono una sottocartella `PDF`
2. Ricerca substring case-insensitive sullo `stem` dei PDF (glob `*.pdf` + `*.PDF`)
3. Solo se DB_DISEGNI restituisce 0 risultati → ricerca in `elaborati_tecnici` leggendo `.pdf_cache.txt`
4. Risultati ordinati per nome, con origine differenziata (verde = DB_DISEGNI, giallo = elaborati_tecnici)

## Cache
- Cartelle valide DB_DISEGNI in cache globale in memoria, TTL 8 ore (28800 s)
- CLI: timestamp persistito su file `.cache_timestamp` (sopravvive ai riavvii)
- Web: cache solo in memoria di processo
- `elaborati_tecnici`: cache testuale `.pdf_cache.txt` generata lato server srv03 da `update_pdf_cache.sh` (richiede `fd`; esclude snapshot, `@eaDir`, `#recycle`; solo PDF modificati nell'ultimo anno)

## Percorsi
- Linux: `/mnt/srv01/DB_DISEGNI`, `/mnt/srv03/elaborati_tecnici` (mount CIFS)
- Windows (solo CLI): `\\srv01\DB_DISEGNI`
- Credenziali Samba: `/etc/samba/credenziali` (chmod 600)

## Struttura
```
apri_disegno/
├── apri_disegno.py          # CLI principale
├── apri_disegno.py.bak      # Backup
├── install.sh               # Installazione automatica Linux Mint
├── git.clone.sh             # Clone repository
├── update_pdf_cache.sh      # Script cache lato srv03
├── etc/                     # fstab.add.txt + samba/credenziali
├── apri_disegno_web/        # App Flask (vedi memoria web_app)
└── .cache_timestamp         # Auto-generato, escluso da git
```

## Installazione client (Linux Mint)
- Repo: https://github.com/rylos/apri_disegno.git → `/home/prod/apri_disegno/`
- `sudo ./install.sh` configura: mount CIFS, 3 icone desktop (Apri Disegno, MES Qualitas, Elaborati Tecnici), avvio automatico, wrapper di riavvio (100 ms), git pull giornaliero alle 6:00 via cron + anacron
- App persistente: terminale 195x59 in alto a sinistra, non chiudibile

## Novità v1.2
Loop sui risultati di `elaborati_tecnici`: dopo l'apertura di un file si torna alla lista, con opzione **R** per una nuova ricerca.
