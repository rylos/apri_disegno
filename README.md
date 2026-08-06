# apri_disegno

Programma Python per ricerca e apertura rapida di disegni PDF da rete aziendale.

## Caratteristiche

- 🔍 **Doppia ricerca** per codice disegno (DB_DISEGNI + elaborati_tecnici)
- 🔁 **Loop risultati** per elaborati_tecnici (opzione R per nuova ricerca)
- 🚀 **Indice in memoria**: ricerca istantanea, senza accessi di rete ripetuti
- 🖥️ **Cross-platform** (Windows/Linux)
- 📂 **Apertura automatica** con programma predefinito
- 🎨 **Colori differenziati** per origine risultati (verde/giallo)
- ⚡ **Zero dipendenze** (solo librerie standard Python)
- 🔧 **Installazione automatica** Linux Mint con script
- 🔄 **App persistente** con riavvio automatico se chiusa
- 📅 **Aggiornamenti automatici** con recupero se il PC era spento (timer systemd)

## Installazione Linux Mint

```bash
# Clona repository
git clone https://github.com/rylos/apri_disegno.git
cd apri_disegno

# Installazione automatica (richiede sudo)
sudo ./install.sh
```

**Cosa installa**:
- Mount automatici CIFS per srv01/DB_DISEGNI e srv03/elaborati_tecnici
- 3 icone desktop: Apri Disegno, MES Qualitas, Elaborati Tecnici
- Avvio automatico app all'accensione PC
- App non chiudibile (riavvio automatico in 100ms)
- Aggiornamenti git pull alle 6:00 (cron + anacron)

## Utilizzo

```bash
python3 apri_disegno.py
```

Inserire codice disegno (es. `F353.01.0005` o `F353.01`) e selezionare il file desiderato.

## Requisiti

- Python 3.6+
- Accesso al percorso di rete `srv01/DB_DISEGNI`
- Accesso al percorso di rete `srv03/elaborati_tecnici`

## Performance

All'avvio l'app costruisce un indice di tutti i PDF e lo tiene in memoria: le
ricerche successive non accedono piu' alla rete.

| | Prima | Ora |
|---|---|---|
| Ricerca | 1,3 - 1,6 s | ~1 ms |

- **Avvio**: ~2 s per indicizzare (~4.500 disegni + ~24.000 elaborati tecnici),
  oppure istantaneo se l'indice su disco e' ancora valido
- **Aggiornamento indice**: in background ogni 15 minuti, senza attese per l'utente
- **Disegni appena pubblicati**: se una ricerca non trova nulla l'indice viene
  ricostruito e la ricerca ripetuta, quindi un disegno nuovo si trova comunque

## Struttura

```
apri_disegno/
├── apri_disegno.py      # Programma principale
├── apri_disegno_web/    # Versione web (Flask + htmx)
├── update_pdf_cache.sh  # Script cache server srv03
├── install.sh           # Installazione automatica Linux Mint
├── README.md            # Questa documentazione
└── .pdf_index.json      # Indice PDF locale (auto-generato)
```

---

**Version 1.3** - Indice in memoria (ricerche ~1000x piu' rapide), conteggio dei
disegni distinto dai file trovati per nome cartella, aggiornamenti automatici
affidabili con timer systemd.