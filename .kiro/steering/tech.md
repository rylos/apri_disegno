# Technology Stack

## Core Technologies

### CLI Application
- **Python 3.6+**: Standard library only (zero external dependencies)
- **Cross-platform**: Windows (`os.startfile`) and Linux (`xdg-open`) support
- **Terminal UI**: Color support detection and ANSI escape codes

### Web Application
- **Backend**: Flask 3.0.0 + Gunicorn (2 workers)
- **Frontend**: htmx 1.9.10 (zero build process)
- **Styling**: Custom CSS with Tokyo Night theme
- **Python**: 3.12 (Docker container)

## Infrastructure

### Deployment
- **Docker**: Multi-stage builds with Python 3.12-slim base
- **Container orchestration**: Docker Compose with CIFS volumes
- **Web server**: Gunicorn with 120s timeout, 2 workers
- **Port**: 5000 (HTTP)

### Network Storage
- **Protocol**: CIFS/SMB mounts
- **Mount points**: `/mnt/srv01/DB_DISEGNI`, `/mnt/srv03/elaborati_tecnici`
- **Authentication**: Samba credentials file (`/etc/samba/credenziali`)

### System Integration
- **Linux**: Automatic installation via `install.sh` script
- **Desktop**: `.desktop` files for GUI integration
- **Autostart**: systemd user session integration
- **Updates**: Cron + anacron for daily git pulls

## Common Commands

### Development
```bash
# CLI application
python3 apri_disegno.py

# Web application (local)
cd apri_disegno_web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Docker Deployment
```bash
# Build image
docker build -t apri_disegno_web:latest .

# Run with compose
docker-compose up -d

# Deploy to remote server
rsync -avz --progress apri_disegno_web/ root@docker:/docker/apri_disegno_web/
```

### System Installation
```bash
# Linux Mint installation
sudo ./install.sh

# Manual CIFS mount
sudo mount -t cifs //srv01.liftingitalia.local/DB_DISEGNI /mnt/srv01/DB_DISEGNI -o credentials=/etc/samba/credenziali
```

## Performance Considerations

- **Cache duration**: 8 hours (28800 seconds)
- **First run**: ~1s (loads folder cache)
- **Subsequent runs**: <100ms (uses cache)
- **Web workers**: 2 Gunicorn workers for concurrent requests