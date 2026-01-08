# Project Structure

## Root Directory Layout

```
apri_disegno/
├── apri_disegno.py          # Main CLI application
├── apri_disegno.py.bak      # Backup of CLI application
├── README.md                # Project documentation
├── .cache_timestamp         # Cache timestamp file (auto-generated)
├── flask.pid                # Flask process ID (auto-generated)
├── install.sh               # Linux Mint installation script
├── git.clone.sh             # Repository cloning script
├── update_pdf_cache.sh      # Cache update script for srv03
├── add.to.readme.txt        # Additional README content
├── apri_disegno_web/        # Web application directory
├── etc/                     # System configuration files
├── .git/                    # Git repository data
├── .kiro/                   # Kiro AI assistant configuration
├── .serena/                 # Serena AI assistant data
└── .amazonq/                # Amazon Q assistant configuration
```

## Web Application Structure (`apri_disegno_web/`)

```
apri_disegno_web/
├── app.py                   # Flask backend application
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose configuration
├── .env                    # Environment variables (not in git)
├── .env.example            # Environment template
├── README.md               # Web app documentation
├── flask.log               # Application logs (auto-generated)
├── templates/
│   └── index.html          # Main HTML template (htmx)
├── static/
│   ├── style.css           # Tokyo Night theme CSS
│   ├── favicon.ico         # Browser favicon
│   ├── favicon.png         # PNG favicon
│   ├── favicon.svg         # SVG favicon
│   └── logo.svg            # AreaLifting logo
└── venv/                   # Python virtual environment (local dev)
```

## Configuration Structure (`etc/`)

```
etc/
├── fstab.add.txt           # fstab entries for CIFS mounts
└── samba/
    ├── credenziali         # Samba authentication credentials
    └── 600.permission.txt  # Permission instructions
```

## AI Assistant Directories

- `.kiro/`: Kiro AI assistant configuration and steering files
- `.serena/`: Serena AI assistant memories and project data
- `.amazonq/`: Amazon Q assistant configuration and subagents

## File Naming Conventions

### Python Files
- **Main modules**: `snake_case.py` (e.g., `apri_disegno.py`)
- **Backup files**: `.bak` extension (e.g., `apri_disegno.py.bak`)

### Configuration Files
- **Docker**: Standard names (`Dockerfile`, `docker-compose.yml`)
- **Environment**: `.env` for secrets, `.env.example` for templates
- **Shell scripts**: `.sh` extension with descriptive names

### Web Assets
- **Templates**: `.html` in `templates/` directory
- **Static files**: Organized by type in `static/` directory
- **Favicons**: Multiple formats (`.ico`, `.png`, `.svg`)

## Cache and Runtime Files

- `.cache_timestamp`: Stores folder cache timestamp (8-hour TTL)
- `flask.pid`: Process ID for running Flask application
- `flask.log`: Application runtime logs
- `__pycache__/`: Python bytecode cache directories

## Network Mount Points (Runtime)

- `/mnt/srv01/DB_DISEGNI`: Primary drawing database
- `/mnt/srv03/elaborati_tecnici`: Technical documents archive

## Key Architectural Patterns

- **Separation of concerns**: CLI and web applications are independent
- **Shared logic**: Both applications use similar search algorithms
- **Configuration externalization**: Environment variables and config files
- **Caching strategy**: Shared 8-hour cache for folder structures
- **Cross-platform compatibility**: OS detection for file operations