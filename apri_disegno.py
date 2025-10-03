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
from pathlib import Path
from typing import List, Tuple

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

def display_results(files: List[Tuple[Path, str]]) -> None:
    """Mostra i risultati in modo ordinato e numerati"""
    print(f"\nTrovati {len(files)} file:")
    print("-" * 80)
    
    # Supporto colori: grassetto + blu
    color_start = "\033[1;34m" if os.name != 'nt' or os.getenv('WT_SESSION') else ""
    color_end = "\033[0m" if color_start else ""
    
    for i, (file_path, filename) in enumerate(files, 1):
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
            search_code = input("\nInserire codice disegno (es. F353.01.0005LL o F353.01): ").strip()
        except KeyboardInterrupt:
            print("\nOperazione annullata")
            break
        
        if not search_code:
            continue
        
        # Percorso di rete
        network_path = get_network_path()
        if not network_path.exists():
            print(f"Percorso di rete non accessibile: {network_path}")
            input("\nPremere INVIO per continuare...")
            continue
        
        # Ricerca cartelle valide
        print("Ricerca cartelle...")
        valid_folders = find_valid_folders(network_path)
        if not valid_folders:
            print("Nessuna cartella valida trovata")
            input("\nPremere INVIO per continuare...")
            continue
        
        # Ricerca file PDF
        print(f"Ricerca file PDF con '{search_code}'...")
        pdf_files = search_pdf_files(valid_folders, search_code)
        
        if not pdf_files:
            print("Nessun file trovato")
            input("\nPremere INVIO per continuare...")
            continue
        
        # Mostra risultati
        display_results(pdf_files)
        
        # Selezione file
        try:
            choice = input(f"\nSelezionare file (1-{len(pdf_files)}, 0=NESSUNO, INVIO=1): ").strip()
            if not choice:
                choice = "1"
            
            index = int(choice)
            if index == 0:
                print("Nessun file selezionato")
            elif 1 <= index <= len(pdf_files):
                selected_file = pdf_files[index-1][0]
                print(f"Apertura: {selected_file.name}")
                
                if not open_pdf(selected_file):
                    print("Errore: impossibile aprire il file")
            else:
                print("Selezione non valida")
                
        except ValueError:
            print("Input non valido")
        except KeyboardInterrupt:
            print("\nOperazione annullata")
            break
        
        # Pausa prima di ricominciare
        input("\nPremere INVIO per continuare...")

if __name__ == "__main__":
    main()
