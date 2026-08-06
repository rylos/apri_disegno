#!/usr/bin/env python3
"""
Web app per ricerca disegni PDF
Flask + htmx

Indice completo in memoria: la ricerca non tocca la rete, la scansione CIFS
avviene solo al primo avvio e poi in background alla scadenza della cache.
"""

import gzip
import io
import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Dict, List, Tuple
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400  # cache static 1 giorno

DB_DISEGNI = Path(os.environ.get("DB_DISEGNI", "/mnt/srv01/DB_DISEGNI"))
ELABORATI_TECNICI = Path(os.environ.get("ELABORATI_TECNICI", "/mnt/srv03/elaborati_tecnici"))
ELABORATI_OLD = Path(os.environ.get("ELABORATI_OLD", "/mnt/srv03/elaborati_tecnici_old"))
CACHE_DURATION = 28800  # 8 ore

# L'archivio storico non viene piu' modificato: TTL lungo, e l'indice si costruisce
# solo alla prima ricerca che lo richiede (~558.000 voci, ~80 MB per worker).
OLD_CACHE_DURATION = 86400  # 24 ore
# Su un archivio cosi' grande un termine generico puo' restituire centinaia di
# migliaia di righe (misurato: "cabine" ne da' 336.185): senza tetto la risposta
# JSON sarebbe da decine di MB.
OLD_MAX_RESULTS = 500

# Percorsi mostrati agli utenti Windows (i mount interni non sono utilizzabili)
WIN_ROOTS: List[Tuple[Path, str]] = [
    (DB_DISEGNI, os.environ.get("WIN_DB_DISEGNI", r"\\srv01\DB_DISEGNI")),
    (ELABORATI_TECNICI, os.environ.get("WIN_ELABORATI_TECNICI", r"\\srv03\elaborati_tecnici")),
    (ELABORATI_OLD, os.environ.get("WIN_ELABORATI_OLD", r"\\srv03\Elaborati_Tecnici_OLD")),
]

# Indice persistito su disco: i worker Gunicorn ripartono a caldo dopo un restart
INDEX_FILE = Path(os.environ.get("INDEX_FILE", "/tmp/apri_disegno_index.json"))

# Indice in memoria. Ogni voce: (nome_file, testo_ricercabile_lower, path_assoluto)
_index: Dict[str, object] = {"db": [], "et": [], "built_at": 0.0}
_index_lock = threading.Lock()
_rebuilding = False

# Indice dell'archivio storico, tenuto separato: e' 23 volte piu' grande degli altri
# due messi insieme, non viene persistito su disco e non esiste finche' qualcuno non
# accende la ricerca nell'archivio.
_old_index: Dict[str, object] = {"old": [], "built_at": 0.0}
_old_lock = threading.Lock()


# ---------------------------------------------------------------- costruzione

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


def build_db_entries() -> List[Tuple[str, str, str]]:
    """Indicizza tutti i PDF di DB_DISEGNI (una sola scansione della rete)"""
    entries = []

    for folder in find_valid_folders(DB_DISEGNI):
        try:
            for pdf_file in folder.iterdir():
                if pdf_file.suffix.lower() == ".pdf":
                    entries.append((pdf_file.name, pdf_file.stem.lower(), str(pdf_file)))
        except (OSError, PermissionError):
            continue

    return entries


def build_cache_entries(base_path: Path) -> List[Tuple[str, str, str]]:
    """Indicizza una share leggendo la cache .pdf_cache.txt generata su srv03.

    Il testo ricercabile e' il percorso relativo, non il solo nome file: e' cosi'
    che la ricerca per commessa trova i disegni di una cartella corrispondente.
    """
    entries = []
    cache_file = base_path / ".pdf_cache.txt"

    try:
        if cache_file.exists():
            for line in cache_file.read_text(errors="replace").splitlines():
                line = line.strip()
                if line:
                    full_path = base_path / line
                    entries.append((full_path.name, line.lower(), str(full_path)))
    except (OSError, PermissionError):
        pass

    return entries


def build_et_entries() -> List[Tuple[str, str, str]]:
    """Indicizza elaborati_tecnici"""
    return build_cache_entries(ELABORATI_TECNICI)


def build_index() -> Dict[str, object]:
    """Costruisce l'indice completo e lo salva su disco"""
    index = {
        "db": build_db_entries(),
        "et": build_et_entries(),
        "built_at": time.time(),
    }
    save_index(index)
    return index


def save_index(index: Dict[str, object]) -> None:
    """Scrittura atomica dell'indice su disco"""
    try:
        tmp = INDEX_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(index))
        tmp.replace(INDEX_FILE)
    except (OSError, PermissionError, TypeError):
        pass


def load_index() -> Dict[str, object]:
    """Carica l'indice da disco se ancora valido, altrimenti lo ricostruisce"""
    try:
        if INDEX_FILE.exists():
            data = json.loads(INDEX_FILE.read_text())
            if (time.time() - data.get("built_at", 0)) < CACHE_DURATION and data.get("db"):
                data["db"] = [tuple(e) for e in data["db"]]
                data["et"] = [tuple(e) for e in data["et"]]
                return data
    except (OSError, ValueError, TypeError):
        pass

    return build_index()


def _rebuild_async() -> None:
    """Ricostruisce l'indice in background; le ricerche continuano sul vecchio"""
    global _index, _rebuilding

    try:
        fresh = build_index()
        with _index_lock:
            _index = fresh
    finally:
        with _index_lock:
            _rebuilding = False


def get_index() -> Dict[str, object]:
    """Indice corrente. Se scaduto avvia il refresh in background senza attendere"""
    global _rebuilding

    with _index_lock:
        index = _index
        stale = (time.time() - index["built_at"]) > CACHE_DURATION
        if stale and not _rebuilding:
            _rebuilding = True
            threading.Thread(target=_rebuild_async, daemon=True).start()

    return index


def get_old_index() -> List[Tuple[str, str, str]]:
    """Indice dell'archivio storico, costruito alla prima richiesta e poi tenuto.

    A differenza dell'indice principale la costruzione e' sincrona: qui non c'e' un
    indice vecchio da restituire nel frattempo, e chi ha acceso la ricerca
    nell'archivio si aspetta il risultato. Costa qualche secondo la prima volta
    (lettura di ~60 MB di cache da CIFS), poi e' in memoria per 24 ore.
    """
    with _old_lock:
        entries = _old_index["old"]
        fresh = (time.time() - _old_index["built_at"]) < OLD_CACHE_DURATION

        if entries and fresh:
            return entries

        _old_index["old"] = build_cache_entries(ELABORATI_OLD)
        _old_index["built_at"] = time.time()

        return _old_index["old"]


# ------------------------------------------------------------------- ricerca

def search_entries(entries: List[Tuple[str, str, str]], search_lower: str, source: str) -> List[dict]:
    """Filtro substring in memoria.

    Per elaborati_tecnici il testo ricercabile è il percorso relativo, quindi un file
    può corrispondere per il nome della cartella (commessa) invece che per il nome file.
    `name_match` distingue i due casi: i match sul nome file vengono mostrati per primi.
    """
    found = [
        {
            "name": name,
            "path": path,
            "source": source,
            "name_match": search_lower in name.lower(),
        }
        for name, haystack, path in entries
        if search_lower in haystack
    ]
    return sorted(found, key=lambda f: (not f["name_match"], f["name"]))


def to_windows_path(path: str) -> str:
    """Converte il mount interno nel percorso UNC utilizzabile dai client Windows"""
    for root, win_root in WIN_ROOTS:
        root_str = str(root)
        if path == root_str:
            return win_root
        if path.startswith(root_str + "/"):
            rest = path[len(root_str) + 1:].replace("/", "\\")
            return f"{win_root}\\{rest}"

    return path.replace("/", "\\")


def is_allowed_path(path: Path) -> bool:
    """Consente solo file dentro i due mount point"""
    try:
        resolved = path.resolve()
    except OSError:
        return False

    for root, _ in WIN_ROOTS:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue

    return False


# ------------------------------------------------------------------- routes

@app.context_processor
def inject_asset_helper():
    """URL degli static con versione da mtime: il browser ricarica subito dopo un deploy
    senza rinunciare alla cache lunga."""
    def asset(filename: str) -> str:
        try:
            version = int((Path(app.static_folder) / filename).stat().st_mtime)
        except OSError:
            version = 0
        return f"/static/{filename}?v={version}"

    return {"asset": asset}


@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Endpoint ricerca"""
    started = time.perf_counter()
    search_term = request.form.get('search_term', '').strip()
    include_old = request.form.get('include_old') in ('1', 'on', 'true')

    if not search_term:
        return jsonify({'error': 'Inserire codice disegno'}), 400

    search_lower = search_term.lower()
    idx = get_index()

    # Cascata: elaborati_tecnici solo se DB_DISEGNI e' a zero, archivio storico
    # solo se anche elaborati_tecnici e' a zero e l'utente lo ha richiesto
    results = search_entries(idx["db"], search_lower, "db_disegni")
    if not results:
        results = search_entries(idx["et"], search_lower, "elaborati_tecnici")

    truncated = 0
    if not results and include_old:
        results = search_entries(get_old_index(), search_lower, "elaborati_old")
        if len(results) > OLD_MAX_RESULTS:
            truncated = len(results) - OLD_MAX_RESULTS
            results = results[:OLD_MAX_RESULTS]

    if not results:
        return jsonify({'error': 'Nessun file trovato'}), 404

    for item in results:
        parent = str(Path(item["path"]).parent)
        item["parent"] = to_windows_path(parent)
        item["parent_unix"] = parent

    return jsonify({
        'files': results,
        'total': len(results),
        'truncated': truncated,
        'elapsed_ms': round((time.perf_counter() - started) * 1000, 1),
    })


@app.route('/pdf/<path:filepath>')
def serve_pdf(filepath):
    """Serve PDF file"""
    pdf_path = Path('/' + filepath)

    if not is_allowed_path(pdf_path):
        return "Accesso non consentito", 403

    if not pdf_path.exists():
        return "File non trovato", 404

    return send_file(pdf_path, mimetype='application/pdf')


@app.route('/stats')
def stats():
    """Stato dell'indice (diagnostica)"""
    idx = get_index()
    age = time.time() - idx["built_at"]

    with _old_lock:
        old_count = len(_old_index["old"])
        old_age = time.time() - _old_index["built_at"] if old_count else None

    return jsonify({
        'db_disegni': len(idx["db"]),
        'elaborati_tecnici': len(idx["et"]),
        'elaborati_old': old_count,
        'elaborati_old_age_seconds': round(old_age) if old_age is not None else None,
        'age_seconds': round(age),
        'rebuilding': _rebuilding,
    })


@app.after_request
def compress(response):
    """Gzip sulle risposte JSON/testuali di dimensione non banale"""
    if (response.direct_passthrough
            or response.status_code < 200
            or response.status_code >= 300
            or 'Content-Encoding' in response.headers
            or 'gzip' not in request.headers.get('Accept-Encoding', '')):
        return response

    ctype = response.headers.get('Content-Type', '')
    if not any(t in ctype for t in ('json', 'javascript', 'text/', 'svg')):
        return response

    data = response.get_data()
    if len(data) < 1024:
        return response

    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6, mtime=0) as gz:
        gz.write(data)

    response.set_data(buf.getvalue())
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = response.content_length
    response.headers.add('Vary', 'Accept-Encoding')

    return response


# Indice caricato all'import: con `gunicorn --preload` i worker nascono già caldi
_index = load_index()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
