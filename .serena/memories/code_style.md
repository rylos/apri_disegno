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
- **Ricerca condizionale**: la fonte secondaria viene interrogata solo se la primaria dà 0 risultati
- **String formatting**: f-string
- **Colori terminale**: ANSI, verde `\033[1;32m` per DB_DISEGNI, giallo `\033[1;33m` per elaborati_tecnici; rilevamento supporto colori via `COLORTERM`, `TERM`, `WT_SESSION`

## Formattazione
- Indentazione 4 spazi, riga ~80 caratteri (non rigida), riga vuota tra le funzioni, doppi apici per le stringhe

## Architettura
- Un solo file per applicazione, funzioni piccole e senza classi
- La logica di ricerca è duplicata (non condivisa) tra CLI e web: **modificando l'una, valutare sempre l'allineamento dell'altra**
- UX CLI: schermo pulito ad ogni operazione, loop continuo, opzione **R** per nuova ricerca sui risultati elaborati_tecnici
