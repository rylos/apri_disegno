# Archivio storico Elaborati_Tecnici_OLD nella web app (2026-08-06)

Richiesta di **Denis Sarzi Braga** (mail 2026-08-06): poter cercare anche in "elaborati old".
Marco ha risposto che sarebbe stato un **interruttore, spento di default**, per pesare meno sul
server. Implementato **solo nella web app** — la CLI non e' stata toccata.

**Stato: in produzione dal 2026-08-06**, commit `4ebc02b`, deploy verificato end-to-end
(`/stats` → 558.013 voci). Interruttore visibile sotto la barra di ricerca, badge `OLD` viola.

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

⚠️ **Gli 81 MB della tabella sono una sottostima**: in produzione sono risultati ~275 MB per
worker, vedi la sezione "Numeri misurati IN PRODUZIONE" qui sotto. La *classifica* fra i tre
metodi resta valida, i valori assoluti no.

## Numeri misurati IN PRODUZIONE (2026-08-06, dopo il deploy)
- Prima ricerca su un worker: **~4,9 s** (build dell'indice). Con 2 worker gunicorn e l'indice
  pigro **non condiviso via fork**, capita **due volte**: la prima ricerca lenta su un worker non
  evita quella sull'altro (osservato: 4,9 s e poi di nuovo 5,9 s su una ricerca diversa).
- Ricerche successive: **57 ms**
- Ricerca sulle fonti correnti: 1,6 ms (invariata)
- **Memoria container: 89 MB → 640 MB** con l'archivio caricato su entrambi i worker.

⚠️ **I 640 MB sono molto piu' degli ~80 MB per worker che il benchmark faceva prevedere** (~275 MB
per worker). Il benchmark sottostimava per due motivi: memorizzava il **percorso relativo** mentre
l'app salva quello **assoluto** (+35 caratteri per voce su 558.013 voci), e il picco di
`splitlines()` su 60 MB di testo non viene restituito al sistema operativo dopo la build.
Il server docker ha 8 GB e ne restano 4,4 liberi, quindi non e' un problema oggi — ma se servisse
ridurre: costruire l'indice con un generatore invece di `splitlines()`, o memorizzare il percorso
relativo e ricomporre quello assoluto solo sui risultati.

## Permessi Samba: l'ostacolo del primo deploy (risolto il 2026-08-06)
Il primo tentativo di deploy e' fallito: l'utente `prod` non aveva accesso alla share
`Elaborati_Tecnici_OLD` (`tree connect failed: NT_STATUS_ACCESS_DENIED`, mount CIFS
`permission denied`). Marco ha concesso il permesso da DSM e il mount e' passato.

🪤 **Un volume CIFS che non monta impedisce l'avvio dell'INTERO container**, non degrada soltanto
quella fonte: il servizio e' rimasto giu' finche' non e' stato ripristinato il compose del backup.
Prima di aggiungere un volume nuovo, verificare sempre l'accesso con:
```bash
smbclient //srv03.liftingitalia.local/<share> -U prod%<pass> -c ls
```

🪤 **`smb.share.conf` non e' la fonte di verita' dei permessi su queste share.** Dopo la concessione
l'accesso funzionava ma il file era **invariato** (`valid users=nobody,nobody`, mtime del 3 agosto):
i permessi sono applicati via **ACL Synology**, non via `valid users`. Diagnosticare un accesso
negato leggendo quel file porta a conclusioni sbagliate — verificare sempre con `smbclient`.

🪤 Il tag di rollback in `mem:suggested_commands` era **sbagliato**: l'immagine in uso e'
`apri_disegno_web-apri_disegno_web:latest` (nome generato da compose), non `apri_disegno_web:latest`.

## Altro
- Volume CIFS `elaborati_tecnici_old` in docker-compose, `ro`, device
  `//srv03.liftingitalia.local/Elaborati_Tecnici_OLD`, montato su `/mnt/srv03/elaborati_tecnici_old`
- `WIN_ROOTS` esteso: l'ordine e' innocuo perche' `elaborati_tecnici_old` non e' sotto
  `elaborati_tecnici` (il carattere dopo il prefisso e' `_`, non `/`)
- `DB_DISEGNI` e `ELABORATI_TECNICI` ora leggibili da variabile d'ambiente come `ELABORATI_OLD`:
  serviva per poter testare in locale senza i mount
- Colore viola Tokyo Night (`#5f4b8b` / `#9d7cd8`), badge `OLD`, icona `i-archive`

Generazione della cache dell'archivio: `mem:cache_pdf_srv03`. Vedi anche `mem:web_app`.
