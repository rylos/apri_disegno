# Comandi Suggeriti - Release 1.1

## Esecuzione programma
```bash
# Esecuzione diretta
python3 apri_disegno.py

# Con permessi di esecuzione
chmod +x apri_disegno.py
./apri_disegno.py
```

## Script cache server (srv03)
```bash
# Esecuzione manuale script cache
./update_pdf_cache.sh

# Verifica cache generata
ls -la /volume1/Elaborati_Tecnici/.pdf_cache.txt
wc -l /volume1/Elaborati_Tecnici/.pdf_cache.txt

# Controllo contenuto cache (prime righe)
head -20 /volume1/Elaborati_Tecnici/.pdf_cache.txt
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
git add apri_disegno.py update_pdf_cache.sh
git commit -m "Descrizione modifiche"

# Push/pull
git push origin main
git pull origin main
```

## Debug e troubleshooting
```bash
# Test accesso percorsi rete
ls -la /mnt/srv01/DB_DISEGNI/
ls -la /mnt/srv03/elaborati_tecnici/.pdf_cache.txt

# Verifica cache locale
ls -la .cache_timestamp
cat .cache_timestamp

# Test ricerca manuale
grep -i "codice" /mnt/srv03/elaborati_tecnici/.pdf_cache.txt
```