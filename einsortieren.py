import os
import shutil
from tkinter import messagebox

def sortiere_bilder(ordner_pfad):
    # Liste aller Dateien im angegebenen Ordner
    dateien = os.listdir(ordner_pfad)

    übersprungen = []

    for datei in dateien:
        datei_pfad = os.path.join(ordner_pfad, datei)

        # Ignoriere Unterordner
        if os.path.isdir(datei_pfad):
            continue

        # Extrahiere Kategorie und Nummer aus dem Dateinamen
        datei_teile = datei.split('_')
        if len(datei_teile) < 2:
            print(f"Die Datei '{datei}' hat nicht das erwartete Format und wird übersprungen.")
            übersprungen.append(datei)
            continue

        kategorie, nummer = datei_teile[0], datei_teile[1]
        
        # Erstelle einen Ordner für die Kategorie, wenn noch nicht vorhanden
        kategorie_ordner = os.path.join(ordner_pfad, kategorie)
        if not os.path.exists(kategorie_ordner):
            os.makedirs(kategorie_ordner)

        # Zielordner für die Datei
        ziel_pfad = os.path.join(kategorie_ordner, datei)

        # Verschiebe die Datei in den Zielordner
        shutil.move(datei_pfad, ziel_pfad)
    
    if len(übersprungen) == 0:
        übersprungen = "Keine Dateien"
    else:
        
        übersprungen = "Einige Dateien"

    print("Bilder erfolgreich sortiert.")
    messagebox.showinfo("Info", f"Bilder sortiert.\n{übersprungen} wurden übersprungen.")


def reverse(ordner_pfad):
    # Liste aller Unterordner im angegebenen Ordner
    unterordner = [d for d in os.listdir(ordner_pfad) if os.path.isdir(os.path.join(ordner_pfad, d))]

    for unterordner_name in unterordner:
        unterordner_pfad = os.path.join(ordner_pfad, unterordner_name)

        # Liste aller Dateien im Unterordner
        dateien = os.listdir(unterordner_pfad)

        for datei in dateien:
            datei_pfad = os.path.join(unterordner_pfad, datei)

            # Zielordner für die Datei im Hauptordner A
            ziel_pfad = os.path.join(ordner_pfad, datei)

            # Verschiebe die Datei in den Zielordner im Hauptordner
            shutil.move(datei_pfad, ziel_pfad)

        # Lösche den leeren Unterordner
        os.rmdir(unterordner_pfad)
    messagebox.showinfo("Info", "Alle Ordner entpackt und gelöscht.",icon="info")


def entferne_bis_vorletzten_unterstrich(datei_pfad):
    # Extrahiere den Dateinamen aus dem Pfad
    dateiname = os.path.basename(datei_pfad)

    # Teile den Dateinamen anhand der Unterstriche
    datei_teile = dateiname.rsplit('_', 1)

    # Überprüfe, ob mindestens ein Unterstrich vorhanden ist
    if len(datei_teile) > 1:
        # Extrahiere den Teil nach dem letzten Unterstrich
        neuer_dateiname = datei_teile[1]

        # Baue den vollständigen Pfad mit dem neuen Dateinamen
        neuer_datei_pfad = os.path.join(os.path.dirname(datei_pfad), neuer_dateiname)

        return neuer_datei_pfad
    else:
        print(f"Die Datei '{dateiname}' hat nicht das erwartete Format oder keinen Unterstrich und wird übersprungen.")
        return None

def kategorisierung_entfernen(ordner_pfad):
    # Liste aller Dateien im angegebenen Ordner
    dateien = os.listdir(ordner_pfad)

    for datei in dateien:
        datei_pfad = os.path.join(ordner_pfad, datei)

        # Ignoriere Unterordner
        if os.path.isdir(datei_pfad):
            continue

        # Wende die Funktion auf jede Datei an
        neuer_datei_pfad = entferne_bis_vorletzten_unterstrich(datei_pfad)

        # Wenn die Funktion erfolgreich angewendet wurde, ändere den Dateipfad
        if neuer_datei_pfad:
            os.rename(datei_pfad, neuer_datei_pfad)
            #print(f"Datei umbenannt: {datei_pfad} zu {neuer_datei_pfad}")

    messagebox.showinfo("Info", "Kategorisierung entfernt.\nWenn du in dieser Sitzung schon Bilder kategorisiert hast,\nist jetzt ein Neustart erforderlich.")


def backup_folder(folder_path):
    # Ensure the provided path is a directory
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return

    # Get the absolute path of the folder to be backed up
    folder_abs_path = os.path.abspath(folder_path)

    # Get the parent directory of the folder to be backed up
    parent_directory = os.path.dirname(folder_abs_path)

    # Get the folder name from the path
    folder_name = os.path.basename(folder_abs_path)

    # Create the backup folder name
    backup_folder_name = f"Backup_{folder_name}"

    # Create the full path for the backup folder in the parent directory
    backup_folder_path = os.path.join(parent_directory, backup_folder_name)

    try:
        # Copy the entire folder to the backup location
        shutil.copytree(folder_abs_path, backup_folder_path)
        print(f"Folder '{folder_abs_path}' successfully backed up to '{backup_folder_path}'.")
    except shutil.Error as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False  
    
#test

