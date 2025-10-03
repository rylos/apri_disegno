# Comandi Suggeriti

## Esecuzione programma
```bash
# Esecuzione diretta
python3 apri_disegno.py

# Con permessi di esecuzione
chmod +x apri_disegno.py
./apri_disegno.py
```

## Sviluppo e testing
```bash
# Verifica sintassi
python3 -m py_compile apri_disegno.py

# Controllo type hints (se mypy installato)
mypy apri_disegno.py

# Formattazione codice (se black installato)
black apri_disegno.py

# Linting (se flake8/ruff installato)
flake8 apri_disegno.py
ruff check apri_disegno.py
```

## Git operations
```bash
# Status e commit
git status
git add apri_disegno.py
git commit -m "Descrizione modifiche"

# Push/pull
git push origin main
git pull origin main
```

## Comandi sistema Linux
```bash
# Navigazione
ls -la
cd /path/to/directory
pwd

# Ricerca file
find . -name "*.py"
grep -r "pattern" .

# Permessi
chmod +x file.py
chown user:group file.py
```