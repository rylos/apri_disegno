# Stile e Convenzioni di Codice

## Stile Python
- **Docstring**: una riga in italiano per ogni funzione
- **Type hints**: su parametri e valori di ritorno (`List[Path]`, `Tuple[Path, str, str]`, `Optional[...]`)
- **Naming**: snake_case per funzioni e variabili; cache globali con prefisso `_` (`_valid_folders_cache`, `_cache_timestamp`)
- **Costanti**: MAIUSCOLE a livello modulo (`DB_DISEGNI`, `CACHE_DURATION`)
- **Imports**: solo standard library nella CLI; nel web solo Flask in aggiunta
- **Commenti**: in italiano, inline sulla logica non ovvia

## Pattern ricorrenti
- **Path handling**: sempre `pathlib.Path`, mai concatenazione di stringhe
- **Cross-platform**: controllo `os.name == 'nt'` per percorsi e apertura file (`os.startfile` vs `xdg-open`)
- **Error handling**: `except (OSError, PermissionError)` — nella CLI con messaggio all'utente, nel web silenzioso (`pass`/`continue`)
- **Ricerca case-insensitive**: `search_term.lower()` confrontato con `pdf_file.stem.lower()`; glob doppio `*.pdf` + `*.PDF` raccolto in un `set` per evitare duplicati su filesystem case-insensitive
- **Ricerca condizionale a cascata**: ogni fonte viene interrogata solo se la precedente dà 0
  risultati. Nella web app i livelli sono tre (DB_DISEGNI → elaborati_tecnici → archivio storico,
  quest'ultimo solo su richiesta esplicita); nella CLI restano due
- **String formatting**: f-string
- **Colori terminale**: ANSI, verde `\033[1;32m` per DB_DISEGNI, giallo `\033[1;33m` per elaborati_tecnici; rilevamento supporto colori via `COLORTERM`, `TERM`, `WT_SESSION`

## Formattazione
- Indentazione 4 spazi, riga ~80 caratteri (non rigida), riga vuota tra le funzioni, doppi apici per le stringhe

## Architettura
- Un solo file per applicazione, funzioni piccole e senza classi
- La logica di ricerca è duplicata (non condivisa) tra CLI e web: **modificando l'una, valutare sempre l'allineamento dell'altra**. Dal 2026-08-06 entrambe usano lo stesso schema: indice in memoria `(percorso, testo_ricercabile_lower)`, refresh in background, distinzione `name_match`
- **Threading**: solo `threading.Thread(daemon=True)` per il refresh dell'indice, stato condiviso protetto da un `Lock`. Nessuna dipendenza esterna, nemmeno nella web app. L'indice dell'archivio storico ha un lock proprio (`_old_lock`) e si costruisce **in modo sincrono**: li' non c'e' un indice vecchio da servire nel frattempo
- **Percorsi da variabile d'ambiente**: `DB_DISEGNI`, `ELABORATI_TECNICI`, `ELABORATI_OLD` hanno un default ma sono sovrascrivibili da env — e' cosi' che si collauda la web app in locale senza i mount CIFS
- **Fonti multiple, una sola funzione**: `build_cache_entries(base_path)` legge la cache `.pdf_cache.txt` di qualunque share; `search_entries()` filtra qualunque lista di voci. Aggiungere una fonte non deve significare duplicare la ricerca
- UX CLI: schermo pulito ad ogni operazione, loop continuo, opzione **R** per nuova ricerca sui risultati elaborati_tecnici
