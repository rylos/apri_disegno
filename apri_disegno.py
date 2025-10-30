#!/usr/bin/env python3
"""
Programma per ricerca e apertura disegni PDF
Cerca file PDF nel percorso di rete srv01/DB_DISEGNI

Copyright (c) 2025 Marco Ziliani
Version: 2025-09-04
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional

# Cache globale per cartelle valide
_valid_folders_cache: Optional[List[Path]] = None
_cache_timestamp: float = 0

def get_network_path() -> Path:
    """Restituisce il percorso di rete corretto per il sistema operativo"""
    if os.name == 'nt':  # Windows
        return Path(r"\\srv01\DB_DISEGNI")
    else:  # Linux
        return Path("/mnt/srv01/DB_DISEGNI")

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

def get_cached_folders(base_path: Path) -> List[Path]:
    """Restituisce cartelle valide dalla cache o le carica se necessario"""
    global _valid_folders_cache, _cache_timestamp
    current_time = time.time()
    
    # Carica timestamp da file se non ancora fatto
    if _cache_timestamp == 0:
        cache_file = Path(".cache_timestamp")
        if cache_file.exists():
            try:
                _cache_timestamp = float(cache_file.read_text().strip())
            except (ValueError, OSError):
                _cache_timestamp = 0
    
    # Ricarica se cache vuota o passate più di 8 ore (28800 secondi)
    if _valid_folders_cache is None or (current_time - _cache_timestamp) > 28800:
        print("Caricamento cache cartelle...")
        _valid_folders_cache = find_valid_folders(base_path)
        _cache_timestamp = current_time
        
        # Salva timestamp su file
        try:
            Path(".cache_timestamp").write_text(str(_cache_timestamp))
        except OSError:
            pass
        
        print(f"Cache caricata: {len(_valid_folders_cache)} cartelle")
    
    return _valid_folders_cache

def search_pdf_files(folders: List[Path], search_term: str) -> List[Tuple[Path, str]]:
    """Cerca file PDF che contengono il termine di ricerca"""
    found_files = []
    search_lower = search_term.lower()
    
    for folder in folders:
        try:
            # Usa set per evitare duplicati su Windows
            pdf_files = set()
            for pattern in ["*.pdf", "*.PDF"]:
                pdf_files.update(folder.glob(pattern))
            
            for pdf_file in pdf_files:
                if search_lower in pdf_file.stem.lower():
                    found_files.append((pdf_file, pdf_file.name))
        except (OSError, PermissionError):
            continue
    
    return sorted(found_files, key=lambda x: x[1])

def search_elaborati_tecnici(search_term: str) -> List[Tuple[Path, str]]:
    """Cerca file PDF nel cache elaborati tecnici"""
    found_files = []
    search_lower = search_term.lower()
    
    if os.name == 'nt':  # Windows
        base_path = Path(r"\\srv03\Elaborati_Tecnici")
        cache_file = base_path / ".pdf_cache.txt"
    else:  # Linux
        base_path = Path("/mnt/srv03/elaborati_tecnici")
        cache_file = base_path / ".pdf_cache.txt"
    
    try:
        if cache_file.exists():
            for line in cache_file.read_text().splitlines():
                line = line.strip()
                if line and search_lower in line.lower():
                    full_path = base_path / line
                    if full_path.exists():
                        found_files.append((full_path, full_path.name))
    except (OSError, PermissionError):
        pass
    
    return sorted(found_files, key=lambda x: x[1])

def display_results(files: List[Tuple[Path, str]]) -> None:
    """Mostra i risultati in modo ordinato e numerati"""
    print(f"\nTrovati {len(files)} file:")
    print("-" * 80)
    
    # Rileva supporto colori
    supports_color = (
        os.getenv('COLORTERM') or 
        os.getenv('TERM', '').endswith('color') or
        os.getenv('WT_SESSION') or
        (os.name != 'nt' and sys.stdout.isatty())
    )
    
    for i, (file_path, filename) in enumerate(files, 1):
        if supports_color:
            # Verde per DB_DISEGNI, giallo per elaborati_tecnici
            if "/mnt/srv01/DB_DISEGNI" in str(file_path):
                color_start = "\033[1;32m"  # Verde
            else:
                color_start = "\033[1;33m"  # Giallo
            color_end = "\033[0m"
        else:
            color_start = color_end = ""
        
        print(f"{i:2d}. {color_start}{filename}{color_end} ({file_path.parent})")
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

def main():
    """Funzione principale"""
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
        network_path = get_network_path()
        if not network_path.exists():
            print(f"Percorso di rete non accessibile: {network_path}")
            time.sleep(2)
            continue
        
        # Ricerca cartelle valide
        print("Ricerca cartelle...")
        valid_folders = get_cached_folders(network_path)
        if not valid_folders:
            print("Nessuna cartella valida trovata")
            time.sleep(2)
            continue
        
        # Ricerca file PDF
        print(f"Ricerca file PDF con '{search_code}'...")
        pdf_files = search_pdf_files(valid_folders, search_code)
        
        # Ricerca elaborati tecnici solo se nessun risultato in DB_DISEGNI
        from_elaborati = False
        if pdf_files:
            all_files = pdf_files
        else:
            print("Ricerca elaborati tecnici...")
            elaborati_files = search_elaborati_tecnici(search_code)
            all_files = elaborati_files
            from_elaborati = True
        
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