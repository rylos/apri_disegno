#!/usr/bin/env python3
"""
Web app per ricerca disegni PDF
Flask + htmx
"""

import re
import time
from pathlib import Path
from typing import List, Tuple
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

# Cache globale
_valid_folders_cache = None
_cache_timestamp = 0

DB_DISEGNI = Path("/mnt/srv01/DB_DISEGNI")
ELABORATI_TECNICI = Path("/mnt/srv03/elaborati_tecnici")
CACHE_DURATION = 28800  # 8 ore

def find_valid_folders(base_path: Path) -> List[Path]:
    """Trova cartelle valide (1 lettera + 3 numeri, no OLD)"""
    pattern = re.compile(r'^[a-zA-Z]\d{3}', re.IGNORECASE)
    folders = []
    
    try:
        for item in base_path.iterdir():
            if (item.is_dir() and 
                pattern.match(item.name) and 
                'OLD' not in item.name.upper()):
                pdf_folder = item / "PDF"
                if pdf_folder.exists():
                    folders.append(pdf_folder)
    except (OSError, PermissionError):
        pass
    
    return folders

def get_cached_folders() -> List[Path]:
    """Restituisce cartelle dalla cache (8h)"""
    global _valid_folders_cache, _cache_timestamp
    current_time = time.time()
    
    if _valid_folders_cache is None or (current_time - _cache_timestamp) > CACHE_DURATION:
        _valid_folders_cache = find_valid_folders(DB_DISEGNI)
        _cache_timestamp = current_time
    
    return _valid_folders_cache

def search_db_disegni(search_term: str) -> List[Tuple[Path, str, str]]:
    """Cerca in DB_DISEGNI"""
    found = []
    search_lower = search_term.lower()
    
    for folder in get_cached_folders():
        try:
            pdf_files = set()
            pdf_files.update(folder.glob("*.pdf"))
            pdf_files.update(folder.glob("*.PDF"))
            for pdf_file in pdf_files:
                if search_lower in pdf_file.stem.lower():
                    found.append((pdf_file, pdf_file.name, "db_disegni"))
        except (OSError, PermissionError):
            continue
    
    return sorted(found, key=lambda x: x[1])

def search_elaborati_tecnici(search_term: str) -> List[Tuple[Path, str, str]]:
    """Cerca in elaborati_tecnici via cache"""
    found = []
    search_lower = search_term.lower()
    cache_file = ELABORATI_TECNICI / ".pdf_cache.txt"
    
    try:
        if cache_file.exists():
            for line in cache_file.read_text().splitlines():
                line = line.strip()
                if line and search_lower in line.lower():
                    full_path = ELABORATI_TECNICI / line
                    if full_path.exists():
                        found.append((full_path, full_path.name, "elaborati_tecnici"))
    except (OSError, PermissionError):
        pass
    
    return sorted(found, key=lambda x: x[1])

@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Endpoint ricerca"""
    search_term = request.form.get('search_term', '').strip()
    
    if not search_term:
        return jsonify({'error': 'Inserire codice disegno'}), 400
    
    # Ricerca DB_DISEGNI
    results = search_db_disegni(search_term)
    
    # Se nessun risultato, cerca elaborati_tecnici
    if not results:
        results = search_elaborati_tecnici(search_term)
    
    if not results:
        return jsonify({'error': 'Nessun file trovato'}), 404
    
    # Prepara risposta
    files = []
    for path, name, source in results:
        files.append({
            'name': name,
            'path': str(path),
            'source': source,
            'parent': str(path.parent)
        })
    
    return jsonify({'files': files})

@app.route('/pdf/<path:filepath>')
def serve_pdf(filepath):
    """Serve PDF file"""
    pdf_path = Path('/' + filepath)
    
    if not pdf_path.exists():
        return "File non trovato", 404
    
    return send_file(pdf_path, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
