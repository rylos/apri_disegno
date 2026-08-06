# Checklist di Completamento Task

## Dopo modifiche alla CLI (`apri_disegno.py`)
1. `python3 -m py_compile apri_disegno.py`
2. Test funzionale:
   - Ricerca con codice completo (`F353.01.0005`) e parziale (`F353.01`)
   - Codice inesistente → deve ricadere su elaborati_tecnici e poi dare "nessun risultato"
   - Apertura PDF da entrambe le fonti
   - Colori corretti (verde DB_DISEGNI / giallo elaborati_tecnici)
   - Loop risultati elaborati_tecnici con opzione **R**
   - Indice: avvio ~2 s la prima volta, istantaneo se `.pdf_index.json` e' fresco; ricerche in millisecondi
   - Codice inesistente: deve ricostruire l'indice ("Aggiornamento indice in corso...") e riprovare
   - La CLI mostra **solo i disegni il cui nome corrisponde**: i file trovati per nome della cartella (commessa) sono filtrati via, davano elenchi lunghi e inutili. La web app invece li mostra, contati a parte: **e' una divergenza voluta fra le due interfacce**

## Dopo modifiche al web (`apri_disegno_web/app.py`)
1. Avvio locale e test di `/`, `/search` (termine valido, vuoto → 400, inesistente → 404), `/pdf/<path>` (fuori dai mount → 403), `/stats`
2. Verificare che i percorsi mostrati siano UNC Windows (`\\srv01\...`) e che il pulsante copia funzioni anche su HTTP
3. Verificare spinner, toggle light/dark, raggruppamento per cartella, evidenziazione termine, scorciatoie `/` ed `Esc`
4. Controllare `elapsed_ms` in risposta: se non è nell'ordine dei millisecondi, l'indice non sta funzionando
5. Build Docker e `docker compose up -d --build`; controllare i log e che i volumi CIFS siano montati read-only

## Dopo modifiche alla CLI: distribuire ai client
La CLI **e'** aggiornabile (vedi [[client_linux_mint]]): commit + push, poi su ognuno dei 4 client
`git pull` e `pkill -f "python3 apri_disegno.py"` (il wrapper riapre la finestra in 100 ms col codice
nuovo). Senza il pkill il processo in esecuzione resta alla versione vecchia.
Verificare sempre tutti e quattro: fino al 2026-08-06 il canale automatico era rotto e un client
era rimasto indietro di 5 mesi.

## Sempre
- La CLI gira in produzione su 4 postazioni: le modifiche vanno testate sul campo prima del rollout Le due implementazioni sono ormai divergenti (la web usa un indice completo in memoria), ma il *comportamento* di ricerca deve restare equivalente: stessa regex cartelle, match substring case-insensitive, fallback su elaborati_tecnici solo a 0 risultati
- Aggiornare `README.md` (e `apri_disegno_web/README.md`) se cambiano funzionalità o versione
- `git status && git diff` prima del commit; messaggio descrittivo in italiano

## Dopo modifiche a `install.sh`
Testare su una macchina Linux Mint pulita: mount CIFS attivi, 3 icone in `/home/prod/Scrivania`, avvio automatico, wrapper di riavvio (100 ms), cron/anacron senza voci duplicate.

## Note operative
- `.env`, `.cache_timestamp`, `flask.pid`, `flask.log`, `venv/` non vanno committati
- Lo script `update_pdf_cache.sh` gira su srv03 e richiede `fd`
- La cache `.pdf_cache.txt` è generata lato server: se elaborati_tecnici non trova nulla, verificare prima la freschezza di quel file
