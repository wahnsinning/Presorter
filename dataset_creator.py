import os
import json
import random 
from pathlib import Path
from typing import List, Dict
import argparse 

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("tqdm nicht installiert. Verwende einfache Prints für Fortschritt.")


def create_dataset(folder_path: str, json_path: str, debug: bool = False, max_per_category: int = 50, use_min_balance: bool = False) -> str:
    
    # Erstellt balancierte JSON-Datei mit Bild-Text-Paaren für CLIP-Fine-Tuning.
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"Ordner nicht gefunden: {folder_path}")
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    
    # Schritt 1: Alle potenziellen Bilddateien sammeln und kategorisieren
    category_files = {}  # {label: [file_paths]}
    if debug:
        print("Zähle und kategorisiere Bilddateien...")
    
    total_potential = 0
    for root, _, files in os.walk(folder_path):
        if debug:
            print(f"Scanne Verzeichnis: {root} ({len(files)} Dateien)")
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                total_potential += 1
                basename = Path(file).stem  
                if '_' in basename:
                    label = basename.split('_')[0].strip()  # Erstes Label vor '_'
                    if label:  # Ignoriere leere Labels
                        file_path = os.path.abspath(os.path.join(root, file))
                        if label not in category_files:
                            category_files[label] = []
                        category_files[label].append(file_path)
    
    if total_potential == 0:
        raise ValueError(f"Keine Bilddateien in {folder_path} gefunden.")
    
    if not category_files:
        raise ValueError(f"Keine gültigen Bilddateien mit Labels in {folder_path} gefunden.")
    
    if debug:
        print(f"Gesamt: {total_potential} potenzielle Bilder -> {len(category_files)} Kategorien gefunden.")
    
    # Schritt 2: Balancieren bestimmen
    if use_min_balance:
        min_count = min(len(files) for files in category_files.values())
        if min_count == 0:
            raise ValueError("Mindestens eine Kategorie ist leer. Kann nicht balancieren.")
        sample_size = min_count
        if debug:
            print(f"Min-Klasse-Größe: {min_count} - Alle Kategorien balanciert auf {min_count} .")
    else:
        sample_size = max_per_category
        if debug:
            print(f"Feste Max pro Kategorie: {max_per_category}.")
    
    # Schritt 3: Dataset bauen mit Sampling und Progress
    dataset: List[Dict[str, str]] = []
    total_sampled = 0
    processed = 0
    pbar = None
    if TQDM_AVAILABLE and total_potential > 10:
        pbar = tqdm(total=total_potential, desc="Bilder verarbeiten", unit="Datei")
    
    for label, files in category_files.items():
        random.shuffle(files)
        sampled = files[:sample_size] 
        
        for img_path in sampled:
            text_prompt = f"{label}"
            dataset.append({'image': img_path, 'text': text_prompt})
        
        total_sampled += len(sampled)
        if debug:
            print(f"Kategorie '{label}': {len(files)} verfügbar -> {len(sampled)} gesampled")
        
        # Progress für alle potenziellen (auch nicht gesampelte)
        processed += len(files)
        if pbar:
            pbar.update(len(files))
        elif debug and not TQDM_AVAILABLE:
            print(f"Fortschritt: {processed}/{total_potential} ({processed/total_potential*100:.1f}%)")
    
    if pbar:
        pbar.close()
    
    if total_sampled == 0:
        raise ValueError(f"Keine ausbalancierten Bilder verfügbar (sample_size zu niedrig?).")
    
    if debug:
        print(f"Gesamt balanciertes Dataset: {total_sampled} Paare aus {len(category_files)} Kategorien.")
    
    # Schritt 4: JSON speichern
    if debug:
        print("Schreibe balancierte JSON...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Balanciertes Dataset erstellt: {json_path} mit {len(dataset)} Paaren.")
    return json_path


# CLI-Wrapper mit argparse 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Erstelle CLIP Dataset aus kategorisiertem Ordner")
    parser.add_argument('folder_path', help="Pfad zum Ordner mit kategorisierten Bildern (Prefix-Labels)")
    parser.add_argument('json_path', nargs='?', default='clip_dataset.json', help="Ausgabe-JSON-Pfad (default: clip_dataset.json)")
    parser.add_argument('--debug', action='store_true', help="Debug-Modus (Logs)")
    parser.add_argument('--max_per_category', type=int, default=50, help="Max. Bilder pro Kategorie (default: 50)")
    parser.add_argument('--use_min_balance', action='store_true', help="Balancieren auf kleinste Kategorie (default: max_per_category)")
    
    args = parser.parse_args()
    
    try:
        create_dataset(
            folder_path=args.folder_path,
            json_path=args.json_path,
            debug=args.debug,
            max_per_category=args.max_per_category,
            use_min_balance=args.use_min_balance
        )
    except ValueError as e:
        print(f"Fehler: {e}")
        exit(1)