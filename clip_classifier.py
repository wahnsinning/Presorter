"""
Zero-Shot-Kategorisierung mit CLIP von OpenAI

Im Presorter benutzt als cc
Verwendung aus presorter.py:
    import clip_classifier as cc
    cc.run_clip_classification_gui(self.image_folder,....)
    

"""


# fremdimporte

import os
from pathlib import Path
from typing import List, Tuple

import tkinter as tk
from tkinter import ttk, messagebox

import torch
import clip 
from PIL import Image

import sys
import shutil
import subprocess
import threading

import json


# eigene importe
import save_cat as sc 

class ClipZeroShotClassifier:

    def __init__(self, device: str | None = None, load_fine_tuned: bool = False, fine_tuned_path: str = 'fine_tuned_clip.pt'):
        
        #Initialisiert CLIP-Classifier
        
        # GPU vorziehen wenn eine vorhanden
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        print(f"[CLIP] Lade Modell auf {self.device}...")
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        
        if load_fine_tuned:
            pt_path = Path(fine_tuned_path)
            if not pt_path.exists():
                print(f"[CLIP] Warnung: Fine-tuned Modell nicht gefunden: {fine_tuned_path}. Verwende Zero-Shot.")
                load_fine_tuned = False  # Fallback
            else:
                # State Dict laden (map_location für Flexibilität)
                state_dict = torch.load(pt_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                print(f"[CLIP] Fine-tuned Modell geladen: {fine_tuned_path}")
        else:
            print("[CLIP] Zero-Shot Modell 'ViT-B/32' geladen (kein Fine-Tuning).")
        
        self.model.eval()  # Eval-Mode für Inference
        print("[CLIP] Modell bereit.")

    def classify_image(
        self,
        image_path: str,
        categories: List[str],
        language: str = "de",
        top_k: int = 3,
    ) -> List[Tuple[str, float]]:
        
        # klassifiziert nur EIN Bild
        
        if not categories:
            raise ValueError("categories darf nicht leer sein")

        # Bild laden
        image = self.preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(
            self.device
        )

        # Text-Prompts
        if language == "de":
            prompts = [f"ein Foto von {label}" for label in categories]
        else:
            prompts = [f"a photo of {label}" for label in categories]

        text_tokens = clip.tokenize(prompts).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image)
            text_features = self.model.encode_text(text_tokens)

            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            logits_per_image = 100.0 * image_features @ text_features.T
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

        indices = probs.argsort()[::-1][:top_k]
        return [(categories[i], float(probs[i] * 100.0)) for i in indices]

    def classify_folder_summary(
        self,
        folder_path: str,
        categories: List[str],
        language: str = "de",
        max_images: int | None = 50,
    ) -> Tuple[dict, List[str]]:
        
        # Klassifiziert MEHRERE Bilder aus einem Ordner und erstellt eine Statistik

        image_files = [
            f
            for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif", ".heic", ))
        ]
        image_files.sort()

        if max_images is not None:
            image_files = image_files[:max_images]

        counts = {cat: 0 for cat in categories}

        for fname in image_files:
            path = os.path.join(folder_path, fname)
            try:
                results = self.classify_image(path, categories, language, top_k=1)
                if results:
                    cat, _ = results[0]
                    counts[cat] = counts.get(cat, 0) + 1
            except Exception as e:
                print(f"[CLIP] Fehler bei {path}: {e}")

        return counts, image_files

def _load_categories_from_csv(csv_path: str) -> List[str]:
    
    #Lese Kategorien aus Kategorien.csv
    #nutzt save_cat.read_from_csv
    # nimmt IMMER die unterste Zeile
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Kategorien-Datei nicht gefunden: {csv_path}")

    rows = sc.read_from_csv(csv_path)
    if not rows:
        raise ValueError(f"Keine Kategorien in CSV: {csv_path}")

    last_row = rows[-1]

    # in Liste umwandeln wenn string
    if isinstance(last_row, str):
        categories = [c.strip() for c in last_row.split(",") if c.strip()]
    else:
        # sonstige typen
        categories = [str(c).strip() for c in last_row if str(c).strip()]

    if not categories:
        raise ValueError(f"Letzte Zeile in CSV enthält keine Kategorien: {csv_path}")

    return categories



def run_clip_classification_gui(
    folder_path: str,
    csv_path: str,
    parent: tk.Tk | tk.Toplevel | None = None,
    max_images: int | None = None,
    on_open_category_folder=None,
    load_fine_tuned: bool = False,  #fine tuned?
    fine_tuned_path: str = 'fine_tuned_clip.pt',  # Pfad zur .pt-Datei
    on_clip_finished: callable = None,
):
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showwarning(
            "CLIP-Klassifikation", "Kein gültiger Bilderordner.", parent=parent
        )
        return

    try:
        categories = _load_categories_from_csv(csv_path)
    except Exception as e:
        messagebox.showerror(
            "CLIP-Klassifikation",
            f"Kategorien konnten nicht aus CSV geladen werden:\n{e}",
            parent=parent,
        )
        return

    # Bildliste vorbereiten
    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"))
    ]
    image_files.sort()
    if max_images is not None:
        image_files = image_files[:max_images]

    total = len(image_files)
    if total == 0:
        messagebox.showinfo("CLIP-Klassifikation", "Keine Bilder im Ordner gefunden.", parent=parent)
        return

    # Progress-Dialog
    dialog = tk.Toplevel(parent)
    dialog.title("CLIP - Klassifikation läuft...")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)

    label = ttk.Label(dialog, text=f"{total} Bilder werden analysiert...", justify="left")
    label.pack(padx=15, pady=(10, 5))

    progress_var = tk.IntVar(value=0)
    progress = ttk.Progressbar(
        dialog,
        orient="horizontal",
        length=300,
        mode="determinate",
        maximum=total,
        variable=progress_var,
        style="info.Horizontal.TProgressbar",
    )
    progress.pack(padx=15, pady=(0, 10))

    # Ergebniscontainer
    result = {
        "counts": None,
        "category_files": None,
        "error": None,
        "done": 0,
        "finished": False,
    }

    def worker():
        try:
            # Fine-Tuning-Parameter übergeben
            classifier = ClipZeroShotClassifier(
                device=None,  # Auto-Detect
                load_fine_tuned=load_fine_tuned,
                fine_tuned_path=fine_tuned_path
            )
            counts = {cat: 0 for cat in categories}
            category_files = {cat: [] for cat in categories}

            for i, fname in enumerate(image_files, start=1):
                path = os.path.join(folder_path, fname)
                try:
                    preds = classifier.classify_image(path, categories, language="de", top_k=1)
                    if preds:
                        cat, _ = preds[0]
                        counts[cat] = counts.get(cat, 0) + 1
                        category_files[cat].append(path)
                except Exception as e:
                    print(f"[CLIP] Fehler bei {path}: {e}")
                result["done"] = i

            result["counts"] = counts
            result["category_files"] = category_files

            # ergebnisse als json speichern 
            results_path = os.path.join(folder_path, 'clip_results.json')
            print(f"[CLIP] Schreibe Ergebnisse nach: {results_path}")
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(category_files, f, ensure_ascii=False, indent=2)
            print(f"[CLIP] Klassifikationsergebnisse gespeichert: {results_path}")

        except Exception as e:
            result["error"] = e
        finally:
            result["finished"] = True

    def open_folder(path: str):
        """Ordner im OS-Dateimanager öffnen."""
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def create_preview_folder(cat: str, files: list[str]) -> str | None:
        
        # Vorschau-Ordner mit Hardlinks
        
        if not files:
            return None

        preview_root = os.path.join(folder_path, "_clip_preview")
        cat_dir = os.path.join(preview_root, cat)
        os.makedirs(cat_dir, exist_ok=True)

        for src in files:
            try:
                base = os.path.basename(src)
                dst = os.path.join(cat_dir, base)
                counter = 1
                stem, ext = os.path.splitext(base)
                while os.path.exists(dst):
                    dst = os.path.join(cat_dir, f"{stem}_{counter}{ext}")
                    counter += 1
                try:
                    os.link(src, dst)
                except OSError:
                    shutil.copy2(src, dst)
            except Exception as e:
                print(f"[CLIP] Fehler beim Erzeugen der Vorschau für {src}: {e}")

        return cat_dir
    
    def show_result_window(counts: dict, category_files: dict):
        #Ergebnisfenster mit Buttons pro Kategorie anzeigen.
        result_win = tk.Toplevel(parent)
        result_win.title("CLIP-Ergebnis nach Kategorien")
        result_win.transient(parent)
        result_win.grab_set()
        result_win.resizable(False, False)

        info = ttk.Label(
            result_win,
            text="Klicke eine Kategorie an, um die zugehörigen Bilder\n"
                 "in einem Vorschau-Ordner zu prüfen.",
            justify="left",
        )
        info.pack(padx=15, pady=(10, 5))

        btn_frame = ttk.Frame(result_win)
        btn_frame.pack(padx=15, pady=(0, 10))

        for cat in categories:
            files = category_files.get(cat, [])
            n = len(files)
            if n == 0:
                continue

            def handler(c=cat):
                files_c = category_files.get(c, [])
                if not files_c:
                    messagebox.showinfo(
                        "CLIP-Vorschau",
                        f"Keine Bilder für Kategorie '{c}'.",
                        parent=parent,
                    )
                    return

                cat_dir = create_preview_folder(c, files_c)
                if cat_dir is None:
                    messagebox.showinfo(
                        "CLIP-Vorschau",
                        f"Keine Bilder für Kategorie '{c}'.",
                        parent=parent,
                    )
                    return

                if on_open_category_folder is not None:
                    # Presorter soll direkt auf diesen Ordner umschalten
                    on_open_category_folder(cat_dir)
                else:
                    # Fallback: einfach im Explorer öffnen
                    open_folder(cat_dir)

            btn = ttk.Button(
                btn_frame,
                text=f"{cat} ({n})",
                command=handler,
            )
            btn.pack(side=tk.TOP, fill=tk.X, pady=2)

        close_btn = ttk.Button(result_win, text="Schließen", command=result_win.destroy)
        close_btn.pack(pady=(0, 10))

    def poll():
        progress_var.set(result["done"])
        label.config(text=f"{result['done']} / {total} Bilder analysiert...")

        if result["finished"]:
            dialog.grab_release()
            dialog.destroy()

            if result["error"] is not None:
                messagebox.showerror(
                    "CLIP-Fehler",
                    f"Fehler während der Klassifikation:\n{result['error']}",
                    parent=parent,
                )
                return
            
            if on_clip_finished:
                on_clip_finished()

            counts = result["counts"] or {}
            category_files = result["category_files"] or {}
            show_result_window(counts, category_files)
        else:
            dialog.after(100, poll)

    threading.Thread(target=worker, daemon=True).start()
    poll()
