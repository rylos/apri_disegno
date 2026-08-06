# App Web - apri_disegno_web (v1.4)

> Dal 2026-08-06 esiste una terza fonte opzionale, l'archivio storico
> `Elaborati_Tecnici_OLD`, con un indice separato e regole proprie: `mem:archivio_storico_old`.
> Endpoint `/search` accetta `include_old` e restituisce anche `truncated`.

## Stack
- **Backend**: Flask 3.0.0 + Gunicorn 21.2.0 (2 worker, timeout 120 s, **`--preload`**), porta 5000
- **Frontend**: htmx 1.9.10 **servito in locale** (`static/htmx.min.js`, niente CDN)
- **CSS**: tema Tokyo Night custom, toggle light/dark via cookie
- **Runtime Docker**: python:3.12-slim

## Architettura dell'indice (differenza chiave dalla CLI)
La CLI mette in cache solo l'**elenco delle cartelle** e fa `glob()` sulla rete ad ogni ricerca.
La web app costruisce invece un **indice completo in memoria** — la ricerca non tocca mai la rete.

- Voce indice: `(nome_file, testo_ricercabile_lower, path_assoluto)`
  - DB_DISEGNI → testo ricercabile = `stem.lower()`
  - elaborati_tecnici → testo ricercabile = riga della cache `.pdf_cache.txt` (path relativo, quindi matcha anche i nomi cartella)
- `_index = {"db": [...], "et": [...], "built_at": ts}`, protetto da `_index_lock`
- Scaduto (8 h) → `get_index()` avvia un thread di rebuild e **restituisce subito l'indice vecchio**: nessuna ricerca resta in attesa
- Persistito su disco (`INDEX_FILE`, default `/tmp/apri_disegno_index.json`, scrittura atomica tmp+rename) → restart a caldo
- Costruito all'import del modulo: con `--preload` gunicorn lo crea una volta nel master e i worker lo ereditano per fork
- Rimosso il check `full_path.exists()` per ogni match ET (era uno `stat` CIFS per risultato); i link morti danno 404 su `/pdf`

**Numeri misurati in produzione (docker, ago 2026)**: ricerca da 0,7–1,1 s → ~1 ms; build indice 0,68 s per ~4.500 PDF DB_DISEGNI + ~24.000 voci ET (42 cartelle valide).

## Percorsi Windows
`to_windows_path()` converte il mount interno in UNC per gli utenti Windows. Il JSON di `/search` restituisce:
- `path` → path interno, usato solo per il link `/pdf`
- `parent` → percorso UNC mostrato in UI (`\\srv01\DB_DISEGNI\F353\PDF`)
- `parent_unix` → mount interno, per debug

Override via env: `WIN_DB_DISEGNI`, `WIN_ELABORATI_TECNICI`.

## Endpoint
- `GET /` → `index.html`
- `POST /search` (form `search_term`) → `{files: [{name, path, source, parent, parent_unix}], total, elapsed_ms}`; 400 se vuoto, 404 se nessun risultato
- `GET /pdf/<path:filepath>` → `send_file`; **403 se il path risolto non è dentro i due mount** (`is_allowed_path`, fix path traversal)
- `GET /stats` → dimensione indice, età in secondi, flag `rebuilding`

## UI
Icone SVG inline via `<symbol>`/`<use>`: disegno (DB) e documento (ET), cartella, copia, check, lente, luna/sole.
Risultati **raggruppati per cartella** con contatore e pulsante copia-percorso (delegazione eventi + `data-path`, mai `onclick` inline: i backslash Windows lo romperebbero); fallback `execCommand('copy')` perché la Clipboard API non è disponibile su HTTP in LAN.
Termine cercato evidenziato con `<mark>` sia nel nome file sia nel percorso. Badge `DB`/`ET`. Toast di conferma. Scorciatoie `/` (focus) e `Esc` (reset). Footer `© 2025-2026 Marco Ziliani`. Tutto l'output è passato da `escapeHtml()`.

**Troncamento percorsi**: fatto in JS (`shortenPath`, mantiene la coda con `…` iniziale). NON usare `direction: rtl` in CSS: riordina i caratteri neutri e sposta il prefisso UNC `\\` in fondo alla stringa.

## Conteggio risultati: match per nome vs per cartella
Su elaborati_tecnici il match avviene sull'intero percorso relativo, quindi un file può finire nei risultati perché il termine sta nel **nome della cartella (commessa)**, non nel nome file. Es. reale: cercando `0630`, 13 file di cui 8 disegni `250630…` e 5 `250840EP…` che stanno nella cartella `...NN250630ESP...`.

Il backend marca ogni risultato con `name_match` e ordina i match sul nome file per primi. La UI distingue i due casi:
- intestazione: **`N disegni trovati`** (solo i `name_match`) + badge separato `+ M file in una cartella corrispondente`; se `N == 0` scrive "nessun disegno con questo codice"
- voci `by-folder`: bordo punteggiato, sfondo trasparente, nome non grassetto
- etichetta `solo cartella` sui gruppi senza alcun match sul nome

È un comportamento **voluto ed ereditato dalla CLI** (permette la ricerca per commessa): non "correggerlo" filtrando via quei risultati.

## Cache busting degli static
`SEND_FILE_MAX_AGE_DEFAULT = 86400` da solo faceva sì che dopo un deploy i browser continuassero a usare il vecchio CSS/JS (bug reale riscontrato: footer senza stile per l'utente). Il context processor `asset()` accoda `?v=<mtime>` a css/js/logo/favicon nel template — **usare sempre `{{ asset('file') }}`, mai `/static/file` diretto**.

## Altre ottimizzazioni
gzip via `after_request` per risposte JSON/testuali > 1 KB (stdlib, nessuna dipendenza aggiuntiva); una sola `iterdir()` con filtro `suffix.lower() == ".pdf"` invece di due `glob()`.

## Deploy — attenzione, lo stack Portainer non esiste più
Il container era stato creato da uno stack Portainer la cui directory (`/data/compose/50/v1`) **non esiste più**. Il deploy si fa ora direttamente da `/docker/apri_disegno_web` con docker compose: i nomi dei volumi (`apri_disegno_web_db_disegni`, `apri_disegno_web_elaborati_tecnici`) coincidono già col nome del progetto compose, quindi vengono riusati senza ricrearli.

Escludere sempre `.env` dall'rsync (contiene le credenziali Samba e non è in git).
Volumi Docker CIFS read-only da `//srv01.liftingitalia.local/DB_DISEGNI` e `//srv03.liftingitalia.local/elaborati_tecnici`, `TZ=Europe/Rome`, `restart: unless-stopped`.

```bash
rsync -avz --progress apri_disegno_web/ root@docker:/docker/apri_disegno_web/
ssh root@docker 'cd /docker/apri_disegno_web && docker compose up -d --build'
```

## Vincolo importante
La CLI (`apri_disegno.py`) **non va modificata**: i client Linux Mint non sono aggiornabili. Le ottimizzazioni sopra sono deliberatamente solo lato web; la logica di ricerca resta funzionalmente equivalente (stessa regex cartelle, stesso match substring case-insensitive, stesso fallback su ET solo a 0 risultati).
