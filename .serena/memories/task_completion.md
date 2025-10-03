# Task Completion Checklist

## Dopo modifiche al codice
1. **Verifica sintassi**
   ```bash
   python3 -m py_compile apri_disegno.py
   ```

2. **Test funzionale**
   - Eseguire il programma
   - Testare ricerca con codici validi/invalidi
   - Verificare apertura PDF

3. **Controllo stile** (opzionale)
   ```bash
   # Se disponibili
   black apri_disegno.py
   flake8 apri_disegno.py
   mypy apri_disegno.py
   ```

## Prima del commit
1. **Verifica modifiche**
   ```bash
   git status
   git diff
   ```

2. **Test completo**
   - Esecuzione senza errori
   - Funzionalità principali operative

3. **Commit con messaggio descrittivo**
   ```bash
   git add apri_disegno.py
   git commit -m "Descrizione chiara delle modifiche"
   ```

## Note importanti
- **Nessun test automatico**: Progetto semplice senza suite di test
- **Dipendenze**: Solo librerie standard, nessun requirements.txt
- **Cross-platform**: Testare su Linux (ambiente principale)
- **Percorso rete**: Verificare accessibilità `/mnt/srv01/DB_DISEGNI`