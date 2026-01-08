# Product Overview

**apri_disegno** is a Python-based PDF drawing search and opening system for corporate network environments.

## Core Functionality

- **Dual search system**: Primary search in `DB_DISEGNI` database, fallback to `elaborati_tecnici` archive
- **Smart caching**: 8-hour intelligent cache system for folder structures to optimize performance
- **Cross-platform support**: Works on both Windows and Linux environments
- **Network file access**: Accesses PDF files via CIFS/SMB network mounts

## Applications

1. **CLI Application** (`apri_disegno.py`): Terminal-based search with color-coded results
2. **Web Application** (`apri_disegno_web/`): Flask-based web interface with htmx frontend

## Target Environment

- Corporate network with Samba/CIFS file shares
- Linux Mint workstations with automatic installation
- Docker deployment for web version
- Network paths: `srv01/DB_DISEGNI` and `srv03/elaborati_tecnici`

## Key Features

- Zero-dependency CLI version (Python standard library only)
- Persistent application with auto-restart capability
- Automatic daily git updates via cron/anacron
- Color-coded search results (green for DB_DISEGNI, yellow for elaborati_tecnici)
- Tokyo Night theme for web interface with light/dark mode toggle