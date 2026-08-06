# apri_disegno_web

Web app per ricerca e visualizzazione disegni PDF da rete aziendale.

## Stack

- **Backend**: Flask + Python 3.12
- **Frontend**: htmx (zero build)
- **Deploy**: Docker + Portainer
- **Theme**: Tokyo Night Light/Dark

## Funzionalità

- 🔍 Ricerca a cascata: DB_DISEGNI → elaborati_tecnici → archivio storico (opzionale)
- ⚡ Indice completo in memoria: ricerca in pochi ms, la rete non viene toccata
- 🪟 Percorsi mostrati in formato UNC Windows (`\\srv01\DB_DISEGNI\...`), copiabili con un click
- 🗂️ Risultati raggruppati per cartella, con icone e badge origine (DB / ET / OLD)
- 🗄️ Archivio storico `Elaborati_Tecnici_OLD` attivabile con un interruttore (default spento)
- ✨ Evidenziazione del termine cercato nel nome file
- ⌨️ Scorciatoie: `/` per cercare, `Esc` per pulire
- 🎨 Theme switcher Tokyo Night (Light/Dark)
- 📂 Apertura PDF in nuova tab
- 🚀 Zero installazione client, zero dipendenze esterne (htmx servito in locale)
- 🎯 Logo AreaLifting e favicon
- 🔄 Mount CIFS automatici
- ⏳ Spinner animato con indicatore ricerca

## Deploy su server Docker

### 1. Copia progetto

```bash
rsync -avz --progress apri_disegno_web/ root@docker:/docker/apri_disegno_web/
```

### 2. Configura credenziali

```bash
ssh root@docker
cd /docker/apri_disegno_web
cat > .env << EOF
SAMBA_USER=prod
SAMBA_PASS=<password>
EOF
```

Variabili opzionali (valori di default):

```
WIN_DB_DISEGNI=\\srv01\DB_DISEGNI
WIN_ELABORATI_TECNICI=\\srv03\elaborati_tecnici
WIN_ELABORATI_OLD=\\srv03\Elaborati_Tecnici_OLD
INDEX_FILE=/tmp/apri_disegno_index.json
```

### 3. Build immagine

```bash
cd /docker/apri_disegno_web
docker build -t apri_disegno_web:latest .
```

### 4. Deploy Portainer

1. Accedi a Portainer
2. Stacks → Add stack
3. Nome: `apri_disegno_web`
4. Web editor → Incolla docker-compose.yml
5. Deploy

### 5. Accesso

```
http://docker.liftingitalia.local:5000
```

## Sviluppo locale

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Accesso: `http://localhost:5000`

## Struttura

```
apri_disegno_web/
├── app.py                 # Flask backend
├── templates/
│   └── index.html         # UI htmx + Tokyo Night theme
├── static/
│   ├── style.css          # CSS Tokyo Night
│   ├── htmx.min.js        # htmx self-hosted (no CDN)
│   ├── favicon.png        # Favicon AreaLifting
│   └── logo.svg           # Logo AreaLifting
├── Dockerfile
├── docker-compose.yml     # CIFS volumes
├── requirements.txt
├── .env.example
└── README.md
```

## Performance

L'app costruisce all'avvio un indice completo dei PDF (nome + percorso) e lo tiene
in memoria: le ricerche non accedono più alla rete.

| | Prima | Ora |
|---|---|---|
| Ricerca | 0,7 – 1,1 s | ~1 ms |
| Scansione rete | ad ogni ricerca | una volta ogni 8 h |

- **Build indice**: ~0,7 s (~4.500 PDF in DB_DISEGNI + ~24.000 voci elaborati_tecnici)
- **Refresh**: in background alla scadenza delle 8 h — nessuna ricerca resta in attesa,
  finché il nuovo indice non è pronto si usa quello vecchio
- **Avvio a caldo**: l'indice è persistito su disco (`INDEX_FILE`, default `/tmp/apri_disegno_index.json`)
  e ricaricato dopo un restart se ancora valido
- **`--preload`**: l'indice viene costruito una sola volta nel master gunicorn e ereditato dai 2 worker
- htmx servito in locale (nessuna richiesta a CDN esterni), static con `Cache-Control` 1 giorno, risposte gzip

Stato dell'indice consultabile su `/stats`.

## Archivio storico (Elaborati_Tecnici_OLD)

La share `Elaborati_Tecnici_OLD` contiene **558.000 PDF**, 23 volte le due fonti correnti
messe insieme. Per non farla pesare su chi non la usa:

- **Interruttore in interfaccia**, spento di default, ricordato per utente in un cookie
  (`include_old`) come il tema
- **Terzo livello della cascata**: viene interrogata solo quando DB_DISEGNI *e*
  elaborati_tecnici non trovano nulla
- **Indice pigro**: costruito alla prima ricerca che lo richiede, non all'avvio. Se nessuno
  accende l'interruttore, il server non paga niente
- **TTL 24 h** (contro le 8 h dell'indice principale): è un archivio, non cambia
- **Non persistito su disco**: si ricostruisce leggendo `.pdf_cache.txt`, il JSON sarebbe da oltre 100 MB
- **Tetto di 500 risultati** (`OLD_MAX_RESULTS`): su un archivio così grande un termine generico
  ne restituisce centinaia di migliaia (`arcate` → 64.814). Oltre il tetto l'interfaccia
  segnala quanti risultati sono stati esclusi

| | valore misurato |
|---|---|
| Voci indicizzate | 558.013 |
| Memoria per worker | ~80 MB |
| Prima ricerca (build indice) | ~4 s da disco locale, di più da CIFS |
| Ricerche successive | 40 – 130 ms |

## Requisiti server

- Docker + cifs-utils
- Accesso rete srv01/srv03
- Credenziali Samba

---

**Version 1.4** - Archivio storico opzionale, indice in memoria, percorsi UNC Windows, risultati raggruppati con icone

