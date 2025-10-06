# apri_disegno

Programma Python per ricerca e apertura rapida di disegni PDF da rete aziendale.

## Caratteristiche

- 🔍 **Ricerca veloce** per codice disegno
- 🚀 **Cache intelligente** con scadenza automatica (8 ore)
- 🖥️ **Cross-platform** (Windows/Linux)
- 📂 **Apertura automatica** con programma predefinito
- ⚡ **Zero dipendenze** (solo librerie standard Python)

## Utilizzo

```bash
python3 apri_disegno.py
```

Inserire codice disegno (es. `F353.01.0005` o `F353.01`) e selezionare il file desiderato.

## Requisiti

- Python 3.6+
- Accesso al percorso di rete `srv01/DB_DISEGNI`

## Performance

- **Prima esecuzione**: Carica cache cartelle (~40 cartelle)
- **Esecuzioni successive**: Utilizza cache per ricerca istantanea
- **Aggiornamento automatico**: Cache si rinnova ogni 8 ore

## Struttura

```
apri_disegno/
├── apri_disegno.py      # Programma principale
├── README.md            # Questa documentazione
└── .cache_timestamp     # Cache timestamp (auto-generato)
```

---

**Version 1.0** - Ottimizzato per velocità e semplicità d'uso.