# Stile e Convenzioni di Codice - Release 1.1

## Stile Python
- **Docstring**: Stile Google/NumPy con descrizione funzione
- **Type hints**: Utilizzati per parametri e return values
- **Naming**: snake_case per funzioni e variabili
- **Imports**: Raggruppati per categoria (standard library)

## Convenzioni specifiche
- **Gestione errori**: Try-catch con messaggi utente chiari
- **Path handling**: Uso di pathlib.Path per cross-platform
- **String formatting**: f-strings per interpolazione
- **Commenti**: Commenti inline per logica complessa
- **Colori terminale**: Rilevamento automatico supporto colori cross-platform

## Pattern utilizzati
- **Cross-platform**: Controllo `os.name` per Windows/Linux
- **Error handling**: Gestione graceful di OSError/PermissionError
- **User interaction**: Input validation e feedback chiaro
- **File operations**: Uso di glob patterns per ricerca file
- **Color detection**: Controllo variabili ambiente (COLORTERM, TERM, WT_SESSION)
- **Conditional search**: Ricerca secondaria solo se primaria fallisce
- **Color coding**: Verde (\033[1;32m) per DB_DISEGNI, giallo (\033[1;33m) per elaborati_tecnici

## Formattazione
- **Indentazione**: 4 spazi
- **Lunghezza linea**: ~80 caratteri (non rigida)
- **Separatori**: Linee vuote tra funzioni
- **Stringhe**: Doppi apici per stringhe, singoli per caratteri
- **UX**: Schermo pulito ad ogni operazione, loop continuo

## Architettura funzioni
- **search_pdf_files()**: Ricerca in cartelle DB_DISEGNI
- **search_elaborati_tecnici()**: Ricerca via cache file .pdf_cache.txt
- **display_results()**: Visualizzazione con colori differenziati per origine
- **Logica condizionale**: Seconda ricerca solo se prima = 0 risultati