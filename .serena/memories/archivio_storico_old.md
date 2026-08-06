# Archivio storico Elaborati_Tecnici_OLD nella web app (2026-08-06)

Richiesta di **Denis Sarzi Braga** (mail 2026-08-06): poter cercare anche in "elaborati old".
Marco ha risposto che sarebbe stato un **interruttore, spento di default**, per pesare meno sul
server. Implementato **solo nella web app** — la CLI non e' stata toccata.

## Perche' l'archivio va trattato diversamente
`\\srv03\Elaborati_Tecnici_OLD` contiene **558.013 PDF** contro i 23.841 di elaborati_tecnici e
i ~4.500 di DB_DISEGNI: **23 volte le due fonti correnti messe insieme**. Caricarlo come le altre
non era proponibile senza precauzioni.

## Scelte, con i numeri che le motivano
- **Terzo livello della cascata**: interrogato solo se DB_DISEGNI *e* elaborati_tecnici danno 0.
- **Interruttore per utente**, cookie `include_old` come il tema, default spento. htmx non invia
  le checkbox non spuntate (verificato nel sorgente di htmx.min.js), quindi il default regge.
  La checkbox sta **fuori dal form** per non spezzarne il layout: serve `hx-include="#include-old"`.
- **Indice pigro e sincrono**: costruito alla prima ricerca che lo richiede. Se nessuno accende
  l'interruttore il server non paga nulla. Sincrono e non in background come l'indice principale
  perche' qui non c'e' un indice vecchio da restituire nel frattempo.
- **TTL 24 h**, non persistito su disco (il JSON sarebbe oltre 100 MB; si rilegge la cache).
- **Tetto `OLD_MAX_RESULTS = 500`**: **indispensabile**, non cosmetico. Misurato: `arcate` →
  64.814 risultati, `2015` → 61.937. Senza tetto la risposta JSON sarebbe da decine di MB.
  Il campo `truncated` dice quanti sono stati esclusi, l'interfaccia lo mostra.

## Scelta della struttura dati — benchmark reale, non a intuito
Stimavo 250-400 MB per la lista di tuple e pensavo servisse un blob di testo. **Misurato invece
81 MB**, e la lista di tuple e' anche la piu' veloce insieme al doppio blob:

| metodo | memoria | ricerca |
|---|---|---|
| lista di tuple (schema gia' in uso) | **81 MB** | 40-50 ms |
| blob unico + regex IGNORECASE | ~0 MB | **500-600 ms** (troppo lento) |
| doppio blob (originale + lower) + `str.find` | 95 MB | 18-130 ms |

Ha vinto la lista di tuple: riusa `search_entries()` **senza una riga di codice di ricerca nuovo**
e mantiene `name_match` gratis. `build_et_entries` e' stato generalizzato in
`build_cache_entries(base_path)`.

## Numeri misurati
- Prima ricerca (build indice): ~4 s da disco locale, di piu' da CIFS
- Ricerche successive: 40-130 ms
- Memoria: ~80 MB per worker gunicorn; essendo pigro **non e' condiviso via fork**, quindi con 2
  worker sono ~160 MB. Il server docker ha 8 GB (4,9 liberi), il container stava a 89 MB.

## Altro
- Volume CIFS `elaborati_tecnici_old` in docker-compose, `ro`, device
  `//srv03.liftingitalia.local/Elaborati_Tecnici_OLD`, montato su `/mnt/srv03/elaborati_tecnici_old`
- `WIN_ROOTS` esteso: l'ordine e' innocuo perche' `elaborati_tecnici_old` non e' sotto
  `elaborati_tecnici` (il carattere dopo il prefisso e' `_`, non `/`)
- `DB_DISEGNI` e `ELABORATI_TECNICI` ora leggibili da variabile d'ambiente come `ELABORATI_OLD`:
  serviva per poter testare in locale senza i mount
- Colore viola Tokyo Night (`#5f4b8b` / `#9d7cd8`), badge `OLD`, icona `i-archive`

Generazione della cache dell'archivio: `mem:cache_pdf_srv03`. Vedi anche `mem:web_app`.
