# Stile e Convenzioni di Codice

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

## Pattern utilizzati
- **Cross-platform**: Controllo `os.name` per Windows/Linux
- **Error handling**: Gestione graceful di OSError/PermissionError
- **User interaction**: Input validation e feedback chiaro
- **File operations**: Uso di glob patterns per ricerca file

## Formattazione
- **Indentazione**: 4 spazi
- **Lunghezza linea**: ~80 caratteri (non rigida)
- **Separatori**: Linee vuote tra funzioni
- **Stringhe**: Doppi apici per stringhe, singoli per caratteri