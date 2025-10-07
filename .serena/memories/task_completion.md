# Task Completion Checklist - Release 1.1

## Dopo modifiche al codice
1. **Verifica sintassi**
   ```bash
   python3 -m py_compile apri_disegno.py
   ```

2. **Test funzionale completo**
   - Eseguire il programma
   - Testare ricerca con codici validi/invalidi
   - Verificare apertura PDF da entrambe le fonti
   - Controllare funzionamento cache DB_DISEGNI
   - Verificare ricerca condizionale (elaborati_tecnici solo se DB_DISEGNI = 0)
   - Testare colori differenziati (verde/giallo)

3. **Controllo stile** (opzionale)
   ```bash
   # Se disponibili
   black apri_disegno.py
   flake8 apri_disegni.py
   mypy apri_disegno.py
   ```

## Prima del commit
1. **Verifica modifiche**
   ```bash
   git status
   git diff
   ```

2. **Test completo doppia ricerca**
   - Esecuzione senza errori
   - Funzionalità principali operative
   - Cache DB_DISEGNI funzionante
   - Ricerca elaborati_tecnici operativa
   - Colori corretti per origine

3. **Commit con messaggio descrittivo**
   ```bash
   git add apri_disegno.py update_pdf_cache.sh install.sh README.md
   git commit -m "Descrizione chiara delle modifiche"
   ```

## Test installazione Linux Mint
1. **Script installazione**
   ```bash
   sudo ./install.sh
   ```

2. **Verifica componenti installati**
   - Mount CIFS funzionanti (/mnt/srv01, /mnt/srv03)
   - 3 icone desktop create in /home/prod/Scrivania
   - App avvio automatico configurato
   - Cron job aggiornamento (senza duplicati)
   - Wrapper riavvio automatico funzionante

3. **Test app persistente**
   - App si avvia automaticamente all'accensione
   - Terminale 195x59 posizionato angolo superiore sinistro
   - Riavvio automatico in 100ms se chiusa
   - Wrapper script previene chiusura definitiva

## Note importanti Release 1.1
- **Doppia ricerca**: DB_DISEGNI (primaria) + elaborati_tecnici (secondaria)
- **Ricerca condizionale**: Seconda ricerca solo se prima = 0 risultati
- **Cache server**: Script `update_pdf_cache.sh` eseguito automaticamente su srv03
- **Cache file**: `/mnt/srv03/elaborati_tecnici/.pdf_cache.txt` (generato da server)
- **Colori**: Verde per DB_DISEGNI, giallo per elaborati_tecnici
- **Performance**: Cache intelligente DB_DISEGNI + cache file elaborati_tecnici
- **Installazione**: Script automatico completo per Linux Mint
- **App persistente**: Wrapper con riavvio 100ms, terminale 195x59
- **Aggiornamenti**: Git pull alle 6:00 (cron + anacron)
- **Dipendenze server**: Script richiede `fd` (find alternative) su srv03
- **Filtri cache**: Esclude snapshot, @eaDir, #recycle - solo PDF modificati ultimo anno