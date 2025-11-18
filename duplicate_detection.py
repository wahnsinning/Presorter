import hashlib
import os
from pathlib import Path
from collections import defaultdict

import tkinter as tk
from tkinter import messagebox, ttk

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}


def _hash_file(file_path: Path, chunk_size: int = 8192) -> str:

    #MD5
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()


def _find_exact_duplicates(folder_path: str) -> dict:

    #Finde exakte Duplikate (vielleicht mach ich später noch eine für ähnliche bilder?)
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Ordner nicht gefunden: {folder_path}")
    
    hash_map = defaultdict(list)
    
    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            file_hash = _hash_file(file_path)
            hash_map[file_hash].append(str(file_path))
    
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    return duplicates


def _delete_duplicates(duplicates: dict) -> int:

    deleted = 0
    for files in duplicates.values():
        for f in files[1:]:
            try:
                os.remove(f)
                deleted += 1
            except Exception:
                pass
    return deleted


def _move_duplicates(duplicates: dict, target_folder: str) -> int:
    # Duplikate in irgendeinen Ordner packen
    target = Path(target_folder)
    target.mkdir(exist_ok=True)
    
    moved = 0
    for files in duplicates.values():
        for f in files[1:]:
            src = Path(f)
            dst = target / src.name
            counter = 1
            while dst.exists():
                dst = target / f"{src.stem}_{counter}{src.suffix}"
                counter += 1
            try:
                src.rename(dst)
                moved += 1
            except Exception:
                pass
    return moved


def run_duplicate_check_gui(folder_path: str, parent: tk.Tk | tk.Toplevel | None = None) -> None:
    
    #Duplikatcheck
    
    duplicates = _find_exact_duplicates(folder_path)
    
    if not duplicates:
        messagebox.showinfo("Duplikat-Check", "Keine Duplikate gefunden.", parent=parent)
        return
    
    # Statistiken
    group_count = len(duplicates)
    dup_files = sum(len(files) - 1 for files in duplicates.values())
    wasted_mb = 0.0
    for files in duplicates.values():
        if not files:
            continue
        size_mb = os.path.getsize(files[0]) / (1024 * 1024)
        wasted_mb += size_mb * (len(files) - 1)
    
    # Dialogfenster
    dialog = tk.Toplevel(parent)
    dialog.title("Duplikat-Check")
    dialog.transient(parent)  # Über Parent-Fenster hängen
    dialog.grab_set()         # Modal machen
    dialog.resizable(False, False)
    
    # Inhalt
    info_text = (
        f"Ordner: {folder_path}\n\n"
        f"Gefundene Duplikat-Gruppen: {group_count}\n"
        f"Duplikat-Dateien: {dup_files}\n"
        f"Geschätzter verschwendeter Speicher: {wasted_mb:.2f} MB\n\n"
        "Was soll mit den Duplikaten passieren?"
    )
    
    label = ttk.Label(dialog, text=info_text, justify="left")
    label.pack(padx=15, pady=10)
    
    # Button-Frame
    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=10)
    
    result = {'action': None}  # um Auswahl zurückzugeben
    
    def on_delete():
        result['action'] = 'delete'
        dialog.destroy()
    
    def on_move():
        result['action'] = 'move'
        dialog.destroy()
    
    def on_cancel():
        result['action'] = 'cancel'
        dialog.destroy()
    
    btn_delete = ttk.Button(btn_frame, text="Duplikate löschen", command=on_delete)
    btn_move = ttk.Button(btn_frame, text="In Ordner verschieben", command=on_move)
    btn_cancel = ttk.Button(btn_frame, text="Abbrechen", command=on_cancel)
    
    btn_delete.grid(row=0, column=0, padx=5)
    btn_move.grid(row=0, column=1, padx=5)
    btn_cancel.grid(row=0, column=2, padx=5)
    
    # Fenster zentrieren
    dialog.update_idletasks()
    if parent is not None:
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        dw = dialog.winfo_width()
        dh = dialog.winfo_height()
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2
        dialog.geometry(f"+{x}+{y}")
    
    # Warten bis Dialog geschlossen ist
    dialog.wait_window()
    
    # Aktion ausführen
    if result['action'] == 'delete':
        deleted = _delete_duplicates(duplicates)
        messagebox.showinfo(
            "Duplikat-Check",
            f"{deleted} Duplikat-Dateien gelöscht.",
            parent=parent
        )
    elif result['action'] == 'move':
        # Zielordner: Unterordner "duplicates" im gleichen Pfad
        target = os.path.join(folder_path, "duplicates")
        moved = _move_duplicates(duplicates, target)
        messagebox.showinfo(
            "Duplikat-Check",
            f"{moved} Duplikat-Dateien nach\n'{target}' verschoben.",
            parent=parent
        )
    else:
        # Abgebrochen
        messagebox.showinfo(
            "Duplikat-Check",
            "Keine Aktion durchgeführt.",
            parent=parent
        )
