# apri_disegno

Programma Python per ricerca e apertura rapida di disegni PDF da rete aziendale.

## Caratteristiche

- 🔍 **Doppia ricerca** per codice disegno (DB_DISEGNI + elaborati_tecnici)
- 🚀 **Cache intelligente** con scadenza automatica (8 ore)
- 🖥️ **Cross-platform** (Windows/Linux)
- 📂 **Apertura automatica** con programma predefinito
- 🎨 **Colori differenziati** per origine risultati (verde/giallo)
- ⚡ **Zero dipendenze** (solo librerie standard Python)
- 🔧 **Installazione automatica** Linux Mint con script
- 🔄 **App persistente** con riavvio automatico se chiusa
- 📅 **Aggiornamenti automatici** git pull giornalieri

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

- **Prima esecuzione**: Carica cache cartelle (~40 cartelle)
- **Esecuzioni successive**: Utilizza cache per ricerca istantanea
- **Aggiornamento automatico**: Cache si rinnova ogni 8 ore

## Struttura

```
apri_disegno/
├── apri_disegno.py      # Programma principale
├── update_pdf_cache.sh  # Script cache server srv03
├── README.md            # Questa documentazione
└── .cache_timestamp     # Cache timestamp (auto-generato)
```

---

**Version 1.1** - Ottimizzato per velocità e semplicità d'uso.