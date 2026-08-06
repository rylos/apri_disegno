#!/usr/bin/env python3
"""
Programma per ricerca e apertura disegni PDF
Cerca file PDF nel percorso di rete srv01/DB_DISEGNI

Copyright (c) 2025 Marco Ziliani
Version: 2026-08-06
"""

import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Durata dell'indice prima di essere ricostruito (in background, senza attese)
INDEX_TTL = 900  # 15 minuti
INDEX_FILE = Path(__file__).resolve().parent / ".pdf_index.json"

# Indice in memoria: elenco di (percorso, testo_ricercabile_lower) per ciascuna fonte.
# Evita di rileggere la rete ad ogni ricerca.
_index: Dict[str, object] = {"db": [], "et": [], "built_at": 0.0}
_index_lock = threading.Lock()
_rebuilding = False


def get_network_path() -> Path:
    """Restituisce il percorso di rete corretto per il sistema operativo"""
    if os.name == 'nt':  # Windows
        return Path(r"\\srv01\DB_DISEGNI")
    else:  # Linux
        return Path("/mnt/srv01/DB_DISEGNI")


def get_elaborati_path() -> Path:
    """Restituisce il percorso elaborati tecnici per il sistema operativo"""
    if os.name == 'nt':  # Windows
        return Path(r"\\srv03\Elaborati_Tecnici")
    else:  # Linux
        return Path("/mnt/srv03/elaborati_tecnici")


def find_valid_folders(base_path: Path) -> List[Path]:
    """Trova cartelle che iniziano con 1 lettera e 3 numeri, escludendo OLD"""
    pattern = re.compile(r'^[a-zA-Z]\d{3}', re.IGNORECASE)
    folders = []

    try:
        for item in base_path.iterdir():
            if (item.is_dir() and
                pattern.match(item.name) and
                'OLD' not in item.name.upper()):
                pdf_folder = item / "PDF"
                if pdf_folder.exists() and pdf_folder.is_dir():
                    folders.append(pdf_folder)
    except (OSError, PermissionError) as e:
        print(f"Errore accesso a {base_path}: {e}")

    return folders


def build_db_entries(base_path: Path) -> List[Tuple[str, str]]:
    """Indicizza tutti i PDF di DB_DISEGNI: (percorso, nome_senza_estensione_lower)"""
    entries = []

    for folder in find_valid_folders(base_path):
        try:
            for pdf_file in folder.iterdir():
                if pdf_file.suffix.lower() == ".pdf":
                    entries.append((str(pdf_file), pdf_file.stem.lower()))
        except (OSError, PermissionError):
            continue

    return entries


def build_et_entries() -> List[Tuple[str, str]]:
    """Indicizza elaborati tecnici dalla cache .pdf_cache.txt generata su srv03.

    Il testo ricercabile e' il percorso relativo completo: un file puo' quindi
    corrispondere per il nome della cartella (commessa) e non del file.
    """
    entries = []
    base_path = get_elaborati_path()
    cache_file = base_path / ".pdf_cache.txt"

    try:
        if cache_file.exists():
            for line in cache_file.read_text(errors="replace").splitlines():
                line = line.strip()
                if line:
                    entries.append((str(base_path / line), line.lower()))
    except (OSError, PermissionError):
        pass

    return entries


def build_index(base_path: Path) -> Dict[str, object]:
    """Costruisce l'indice completo delle due fonti e lo salva su disco"""
    index = {
        "db": build_db_entries(base_path),
        "et": build_et_entries(),
        "built_at": time.time(),
    }

    try:
        tmp = INDEX_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(index))
        tmp.replace(INDEX_FILE)
    except (OSError, TypeError):
        pass

    return index


def load_index(base_path: Path) -> Dict[str, object]:
    """Carica l'indice da disco se ancora valido, altrimenti lo ricostruisce.

    Serve a rendere istantanea la riapertura dell'app (il wrapper la rilancia
    ogni volta che l'utente chiude la finestra).
    """
    try:
        if INDEX_FILE.exists():
            data = json.loads(INDEX_FILE.read_text())
            if (time.time() - data.get("built_at", 0)) < INDEX_TTL and data.get("db"):
                data["db"] = [tuple(e) for e in data["db"]]
                data["et"] = [tuple(e) for e in data["et"]]
                return data
    except (OSError, ValueError, TypeError):
        pass

    return build_index(base_path)


def _rebuild_async(base_path: Path) -> None:
    """Ricostruisce l'indice in background: nessuna ricerca resta in attesa"""
    global _index, _rebuilding

    try:
        fresh = build_index(base_path)
        with _index_lock:
            _index = fresh
    except Exception:
        pass
    finally:
        with _index_lock:
            _rebuilding = False


def get_index(base_path: Path, force: bool = False) -> Dict[str, object]:
    """Indice corrente.

    Se scaduto avvia l'aggiornamento in background e restituisce subito quello
    vecchio. Con force=True ricostruisce e attende: serve quando una ricerca non
    ha dato risultati, cosi' un disegno appena pubblicato viene comunque trovato.
    """
    global _index, _rebuilding

    if force:
        fresh = build_index(base_path)
        with _index_lock:
            _index = fresh
        return fresh

    with _index_lock:
        index = _index
        scaduto = (time.time() - index["built_at"]) > INDEX_TTL
        if scaduto and not _rebuilding:
            _rebuilding = True
            threading.Thread(target=_rebuild_async, args=(base_path,), daemon=True).start()

    return index


def search_entries(entries: List[Tuple[str, str]], search_term: str) -> List[Tuple[Path, str, bool]]:
    """Filtra l'indice in memoria.

    Restituisce (percorso, nome_file, corrisponde_il_nome_file). L'ultimo campo
    distingue i disegni veri dai file che stanno solo in una cartella che
    corrisponde alla ricerca.
    """
    search_lower = search_term.lower()
    found = []

    for path_str, haystack in entries:
        if search_lower in haystack:
            path = Path(path_str)
            found.append((path, path.name, search_lower in path.name.lower()))

    # Prima i disegni che corrispondono per nome file, poi gli altri
    return sorted(found, key=lambda x: (not x[2], x[1]))


def supports_color() -> bool:
    """Rileva il supporto ai colori del terminale"""
    return bool(
        os.getenv('COLORTERM') or
        os.getenv('TERM', '').endswith('color') or
        os.getenv('WT_SESSION') or
        (os.name != 'nt' and sys.stdout.isatty())
    )


def display_results(files: List[Tuple[Path, str, bool]]) -> None:
    """Mostra i risultati numerati"""
    print(f"\nTrovati {len(files)} disegni:")
    print("-" * 80)

    colori = supports_color()

    for i, (file_path, filename, _) in enumerate(files, 1):
        if colori:
            if "DB_DISEGNI" in str(file_path):
                colore = "\033[1;32m"     # Verde: DB_DISEGNI
            else:
                colore = "\033[1;33m"     # Giallo: elaborati tecnici
            fine = "\033[0m"
        else:
            colore = fine = ""

        print(f"{i:2d}. {colore}{filename}{fine} ({file_path.parent})")

    print("-" * 80)


def open_pdf(file_path: Path) -> bool:
    """Apre il PDF con il programma predefinito"""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(str(file_path))
        else:  # Linux
            subprocess.run(['xdg-open', str(file_path)], check=True)
        return True
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Errore apertura file: {e}")
        return False


def cerca(base_path: Path, search_code: str) -> Tuple[List[Tuple[Path, str, bool]], bool]:
    """Esegue la ricerca sulle due fonti.

    Su elaborati_tecnici il testo indicizzato e' il percorso relativo, quindi la
    ricerca prenderebbe anche tutti i file contenuti in una cartella (commessa)
    il cui nome corrisponde: elenchi lunghi e inutili. Qui vengono tenuti solo i
    file il cui NOME corrisponde davvero, cioe' i disegni veri.

    Se nessuna delle due fonti da' risultati, ricostruisce l'indice e riprova una
    sola volta: copre il caso del disegno pubblicato da pochi minuti.
    """
    for tentativo in (1, 2):
        index = get_index(base_path, force=(tentativo == 2))

        risultati = search_entries(index["db"], search_code)
        if risultati:
            return risultati, False

        risultati = [r for r in search_entries(index["et"], search_code) if r[2]]
        if risultati:
            return risultati, True

        if tentativo == 1:
            print("Aggiornamento indice in corso...")

    return [], False


def main():
    """Funzione principale"""
    global _index

    network_path = get_network_path()

    # Indice pronto prima della prima ricerca (da disco se ancora valido)
    if network_path.exists():
        print("Caricamento indice disegni...")
        _index = load_index(network_path)
        print(f"Indice pronto: {len(_index['db'])} disegni, {len(_index['et'])} elaborati tecnici")

    while True:
        # Pulisce schermo e mostra prompt
        os.system('clear' if os.name != 'nt' else 'cls')
        print("=== RICERCA DISEGNI PDF ===")

        # Input codice disegno
        try:
            search_code = input("\nInserire codice disegno (es. F353.01.0005LL o 250728FC): ").strip()
        except KeyboardInterrupt:
            print("\nOperazione annullata")
            break

        if not search_code:
            continue

        # Percorso di rete
        if not network_path.exists():
            print(f"Percorso di rete non accessibile: {network_path}")
            time.sleep(2)
            continue

        # L'indice puo' non essere ancora stato costruito (rete assente all'avvio)
        with _index_lock:
            indice_vuoto = not _index["db"] and not _index["et"]
        if indice_vuoto:
            print("Caricamento indice disegni...")
            _index = load_index(network_path)

        print(f"Ricerca file PDF con '{search_code}'...")
        all_files, from_elaborati = cerca(network_path, search_code)

        if not all_files:
            print("Nessun file trovato")
            time.sleep(2)
            continue

        # Loop risultati - ripropone solo se da elaborati_tecnici
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            display_results(all_files)

            try:
                if from_elaborati:
                    choice = input(f"\nSelezionare file (1-{len(all_files)}, 0=NESSUNO, R=NUOVA RICERCA, INVIO=1): ").strip()
                    if choice.upper() == 'R':
                        break
                else:
                    choice = input(f"\nSelezionare file (1-{len(all_files)}, 0=NESSUNO, INVIO=1): ").strip()

                if not choice:
                    choice = "1"

                index = int(choice)
                if index == 0:
                    print("Nessun file selezionato")
                elif 1 <= index <= len(all_files):
                    selected_file = all_files[index-1][0]
                    print(f"Apertura: {selected_file.name}")

                    if not open_pdf(selected_file):
                        print("Errore: impossibile aprire il file")
                else:
                    print("Selezione non valida")

            except ValueError:
                print("Input non valido")
            except KeyboardInterrupt:
                print("\nOperazione annullata")
                return

            # Se non da elaborati_tecnici, esce dopo una selezione
            if not from_elaborati:
                time.sleep(2)
                break

            time.sleep(1)


if __name__ == "__main__":
    main()
