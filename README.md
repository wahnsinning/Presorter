P R E S O R T E R 

Ein Werkzeug zur effizienten manuellen Kategorisierung von Bildern mit einer modernen, vollbildfähigen GUI.


Über das Projekt

Presorter ist eine Desktop-Anwendung, die das manuelle Sortieren großer Bildmengen vereinfacht. Sie ermöglicht die schnelle Kategorisierung durch Hinzufügen von Kategorie-Präfixen zu Dateinamen.


Hauptfunktionen

- Intuitive Bildanzeige mit Vollbildmodus
- Dynamische Kategorien - Füge beliebig viele Kategorien hinzu
- Thumbnail-Vorschau der vorherigen und kommenden Bilder
- Undo-Funktion
- Bildrotation
- Fortschrittsanzeige
- Automatisches Backup vor dem Sortiervorgang
- Batch-Operationen zum Sortieren in Ordner, Entpacken und Zurücksetzen

Installation

Voraussetzungen

- Python 3.8 oder höher
- Windows (aufgrund spezifischer Windows-API-Aufrufe)

Setup

1. Repository klonen:
git clone https://github.com/wahnsinning/Presorter.git
cd Presorter


2. Virtuelle Umgebung erstellen und aktivieren:
python -m venv .venv
.venv\Scripts\activate


3. Abhängigkeiten installieren:
pip install -r requirements.txt



Dependencies

tkinter
ttkbootstrap
Pillow



Verwendung

Starten der Anwendung

python Presorter/presorter.py



Workflow

1. Setup-Fenster: Beim ersten Start wähle aus, ob ein Backup erstellt und gespeicherte Kategorien geladen werden sollen
2. Ordner auswählen: Wähle den Ordner mit den zu sortierenden Bildern
3. Kategorisieren: 
   - Klicke auf einen Kategorie-Button, um das aktuelle Bild zu kategorisieren
   - Oder füge neue Kategorien über das Eingabefeld hinzu
4. Navigation: Nutze die Thumbnail-Vorschau oder die Undo-Funktion
5. Abschluss: Sortiere die kategorisierten Bilder in Ordner mit den oben rechts verfügbaren Buttons

Tastenkombinationen

| Taste       | Funktion 
|-------------|---------------------------------------
| `Enter`     | Neue Kategorie hinzufügen 
| `Strg + R`  | Bild um 90° drehen 
| `←` (Links) | Letzte Aktion rückgängig machen 
| `ESC`       | Vollbildmodus umschalten 

Projektstruktur

Presorter/
├── Presorter/
│ ├── presorter.py 	# Hauptanwendung
│ ├── setup.py 	# Setup-Fenster
│ ├── manager.py 	# Kategorieverwaltung
│ ├── save_cat.py 	# CSV-Speicherverwaltung
│ ├── einsortieren.py 	# Batch-Operationen
│ └── icons/ 		# UI-Icons
├── Kategorien.csv 	# Gespeicherte Kategorien
├── requirements.txt 	
└── README.md


Konfiguration

Kategorien speichern

Kategorien werden automatisch in `Kategorien.csv` gespeichert. Die Datei wird beim ersten Start erstellt und kann für zukünftige Sitzungen wiederverwendet werden.

Themes

Die Anwendung nutzt das "solar" Theme von ttkbootstrap. Andere Themes können durch Ändern des `theme`-Parameters aktiviert werden:

app = Presorter(root, theme='darkly') # Alternativen: 'flatly', 'cyborg', etc.



Bekannte Probleme

- Administrator-Rechte: Die Anwendung fordert Admin-Rechte an, funktioniert aber auch ohne
- Skip-Button: Derzeit deaktiviert, weil das den prozessablauf verkompliziert und evtl die Usability behindert
- Plattform: Nur für Windows


Verbesserungsvorschläge

- Entfernung der unnötigen Admin-Rechte-Anforderung
- Refactoring: Trennung von UI und Geschäftslogik
- Cross-Platform-Support (Linux, macOS)
- Konfigurationsdatei statt CSV (YAML/TOML)

Lizenz: MIT-Lizenz 

Autor

Silas Sinning

Erstellt: 2023
Mit Unterstützung von: ChatGPT-3
