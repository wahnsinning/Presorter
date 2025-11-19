# P R E S O R T E R

Ein Werkzeug zur effizienten manuellen und KI-gestützten Kategorisierung von Bildern mit einer modernen, vollbildfähigen GUI.

Über das Projekt

Presorter ist eine Desktop-Anwendung, die das Sortieren großer Bildsammlungen vereinfacht. Sie kombiniert manuelles Labelling durch Prefix-Änderungen an Dateinamen mit KI-Unterstützung via CLIP für Zero-Shot-Klassifikation. Nach erster Manueller Sichtung der kategorisierten Daten ist ein Fine-Tuning des Modells auf benutzerdefinierten Datasets möglich. Das Tool ist lokal und offline, schützt die Privatsphäre und eignet sich ideal für chaotische Foto-Ordner.​

### Hauptfunktionen

Intuitive Bildanzeige mit Vollbildmodus und Thumbnail-Vorschau (vorherige/nächste drei Bilder)

Dynamische Kategorien: Beliebig viele laden, manuell hinzufügen oder via Eingabefeld erweitern

Undo-Funktion und History für Aktionen

Bildrotation und Navigation (Pfeiltasten)

Fortschrittsanzeige mit Progress-Bar 

Automatisches Backup vor Sortiervorgängen

Sortieren in Ordner, Prefix-Entfernen und Zurücksetzen

KI-Integration: OpenAI CLIP für Zero-Shot-Klassifikation

AI-Labelling: Button zum Akzeptieren von CLIP-Vorschlägen

Duplicate-Detection: MD5-basierte Erkennung und Entfernung von Duplikaten

Fine-Tuning: PyTorch-basiertes Training auf generierten Datasets


### Voraussetzungen

Python 3.8 oder höher
Windows
Git

### Setup

1. Repository klonen:
git clone https://github.com/wahnsinning/Presorter.git
cd Presorter


2. Virtuelle Umgebung erstellen und aktivieren:
python -m venv .venv
.venv\Scripts\activate


3. Bibliotheken installieren:
pip install -r requirements.txt

(Erster Start von CLIP lädt Modelle herunter: Internet erforderlich, danach offline)


### Workflow

1. Setup-Fenster: 
   Beim ersten Start wähle Backup-Erstellung und Kategorien-Laden

2. Ordner auswählen: 
   Wähle den Bildordner

3. Kategorien einstellen: 
   Füge deine persönlichen Kategorien hinzu oder entferne sogar die Default-Kategorien (In letzterem Fall ist "Kategorien speichern" und ein Neustart des Programms erforderlich. Beim nächsten Start sollte "Kategorien laden" angeklickt werden)

4. KI-gestützte Vorkategorisierung:
   (Zero-shot, nicht ganz präzise, je nachdem wie abstrakt die Kategorien sind)
   Es empfiehlt sich, bei großen Datenmengen für diese Vorkategorisierung nur einen Teil zu benutzen, da dieser Teil manuell gesichtet und korrigiert werden sollte, um das Modell optimal zu finetunen. (Das kann Zeit beanspruchen.) (Keine Sorge, auch bei einem geringen Datenset wird das Modell schon gut (bis zu +20% Accuracy gegenüber Zero-Shot) trainiert, da die wenigen verfügbaren Daten augmentiert werden. Wichtig ist allerdings zu wissen, dass die Größe der Kategorie mit den wenigsten Bildern ausschlaggebend für die maximale Anzahl der verwendeten Bilder der übrigen Kategorien ist.(Balancing) Die kleinste Kategorie sollte mindestens 10 Bilder enthalten.)

   - Button "CLIP Kategorienvorschau" um die Kategorisierung zu starten. Es öffnet sich ein Fenster mit der Vorschau über wie viele Bilder in jeder Kategorie vorhanden sind. Die können jetzt einzeln inspiziert werden, aber besser ist, man schließt dieses Fenster erst und klickt... 

   - "AI-Labelling akzeptieren": Das wendet Vorschläge an und labelt alle Dateien automatisch

5. Manuelle Sichtung

   - "In Ordner Sortieren"

   - "Anderen Ordner Öffnen" und Kategorie zur Sichtung auswählen, kurz drüber fliegen, ggf. neu Kategorisieren mit der zuvor genannten Methode. Idealerweise alle Kategorien durchgehen und die bilder so gut kategorisieren wie möglich.

6. Finetuning 
   Wenn alles fertig kategorisiert ist und du dir sicher bist, dass wenig bis keine unpassenden Bilder in den jeweiligen Kategorien liegen, drücke auf...

   - "CLIP-Finetuning starten": Das Modell ändert nun seine Gewichte, um beim nächsten Mal besser zu erkennen, was in welche Kategorie sortiert werden soll.

7. Große Dateisortierungen
   Jetzt kannst du zu riesigen Dateiordnern wechseln, unübersichtlich benannte Ordner mit einem Klick automatisiert entpacken, alle Bilder mit deinem speziell personalisierten Modell klassifizieren, sie mit einem Klick automatisiert in Ordner sortieren, vielleicht stichprobenartig die Kategorisierungen inspizieren; Zack fertig: Übersichtiliche Dateien auf deiner Festplatte :)


### Weitere Tools:

"Duplikatprüfung": MD5-Scan und Entfernung

"Dateinamen zurücksetzen": Sortierung rückgängig machen


### Tastenkombinationen

| Taste              | Funktion 
|--------------------|---------------------------------------
| `Enter`            | Neue Kategorie hinzufügen 
| `Strg + R`         | Bild um 90° drehen 
| `Pfeiltaste Links` | Letzte Aktion rückgängig machen 
| `ESC`              | Vollbildmodus umschalten 



### Themes

Die Anwendung nutzt das "solar" Theme von ttkbootstrap. Andere Themes können durch Ändern des `theme`-Parameters aktiviert werden:

app = Presorter(root, theme='darkly') # Alternativen: 'flatly', 'cyborg', etc.



### Bekannte Probleme

- Skip-Button: Derzeit deaktiviert, weil das den prozessablauf verkompliziert und evtl die Usability behindert
- Plattform: Nur für Windows



### Rechtliches

Lizenz: MIT-Lizenz

Autor: Silas Sinning

Hauptprogramm erstellt: 2023
Mit Unterstützung von: ChatGPT-3

KI-Integration erstellt: 2025
Mit Unterstützung von GROK 4
