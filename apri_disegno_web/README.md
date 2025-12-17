# apri_disegno_web

Web app per ricerca e visualizzazione disegni PDF da rete aziendale.

## Stack

- **Backend**: Flask + Python 3.12
- **Frontend**: htmx (zero build)
- **Deploy**: Docker + Portainer
- **Theme**: Tokyo Night Light/Dark

## Funzionalità

- 🔍 Ricerca doppia: DB_DISEGNI → elaborati_tecnici
- 🎨 Theme switcher Tokyo Night (Light/Dark)
- 📂 Apertura PDF in nuova tab
- ⚡ Cache 8h condivisa tra utenti
- 🚀 Zero installazione client
- 🎯 Logo AreaLifting e favicon
- 🔄 Mount CIFS automatici

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
│   ├── favicon.png        # Favicon AreaLifting
│   └── logo.svg           # Logo AreaLifting
├── Dockerfile
├── docker-compose.yml     # CIFS volumes
├── requirements.txt
├── .env.example
└── README.md
```

## Performance

- Prima richiesta: ~1s (carica cache cartelle)
- Richieste successive: <100ms
- Cache automatica 8h
- 2 worker gunicorn

## Requisiti server

- Docker + cifs-utils
- Accesso rete srv01/srv03
- Credenziali Samba

---

**Version 1.0** - Flask + htmx + Tokyo Night

