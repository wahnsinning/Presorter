import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
import csv
#import queue

import manager as ma

class SetupWindow:
    def __init__(self, root, theme=None):

        #done=False
        self.root = root
        self.root.title("Setup")
        self.style = ttkb.Style(theme=theme)


        self.create_widgets()

    def create_widgets(self):


        #for checking if the buttons exist when destroying them
        self.label_load1 = None
        self.label_load = None
        self.label = None
        self.load_checkbox = None
        self.continue_button = None
        self.backup_checkbox = None
        
        self.label = ttk.Label(self.root, text=''.join(self.willkommensnachricht()),font=("Arial", 12),justify='center')
        self.label.pack(pady=10, side=tk.TOP, expand=True)

        self.backup_var = tk.BooleanVar()
        self.backup_checkbox = ttk.Checkbutton(self.root, text="Sicherheitskopie des Ordners erstellen (smart)", variable=self.backup_var)
        self.backup_checkbox.pack(pady=5)

        if self.check_csv():

            self.label_load = ttk.Label(self.root, text='Darf es außerdem eine Wiederherstellung der gespeicherten Kategorien sein?',font=("Arial", 12), anchor='center')
            self.label_load.pack( fill=tk.X,pady=10, side=tk.TOP, expand=True)

            self.load_var = tk.BooleanVar()
            self.load_checkbox = ttk.Checkbutton(self.root, text="Letzte gespeicherte Kategorien laden", variable=self.load_var)
            self.load_checkbox.pack(pady=25)
        else:
            self.label_load = ttk.Label(self.root, text="Das ist ratsam, wenn man davon ausgeht, dass man sich eine chaotische Kategorisierung zusammenfriemeln könnte.\nVor dem Verlust von Bildern musst du aber keine Angst haben.",font=("Arial", 12),anchor='center')
            self.label_load.pack( fill=tk.BOTH,pady=10, side=tk.TOP, expand=True)

            self.load_var = tk.BooleanVar()
            self.load_checkbox = ttk.Checkbutton(self.root, text="Gespeicherte Kategorien laden", variable=self.load_var, state=tk.DISABLED)
            self.load_checkbox.pack(pady=5)

            self.label_load1 = ttk.Label(self.root, text='Diese Option ist noch nicht verfügbar, weil du noch keine Kategorien gespeichert hast.',font=("Arial", 12),anchor='center')
            self.label_load1.pack( fill=tk.BOTH,pady=10, side=tk.TOP, expand=True)


        self.continue_button = ttk.Button(self.root, text="Volle Möhre", command=self.continue_setup)
        self.continue_button.pack(pady=5)

    
    def continue_setup(self):
        if self.backup_var.get():
            # Add code for creating a backup here
            messagebox.showinfo("Info", "Es wird eine Sicherheitskopie erstellt")
        else:
            messagebox.showinfo("Question", "Es wird KEINE Sicherheitskopie erstellt")
        self.destroy_window()

    def check_backup(self):
        if self.backup_var.get():
            return True
        else:
            return False
        
    def check_load(self):
        if self.load_var.get():
            return True
        else:
            return False

    def check_csv(self):
        with open('Kategorien.csv', 'r') as file:
            reader = csv.reader(file)
            lines = list(reader)
            if len(lines) > 0:
                return True
            else:
                return False
            
    def willkommensnachricht(self):
        willkommensnachricht=[]
        if self.check_csv():
            willkommensnachricht="Willkommen zurück! \n\nMöchtest du eine Sicherungskopie erstellen?"
        else:
            willkommensnachricht=["Neu hier? Na Moin! \n\n",
                                  "Mit diesem Programm kannst du deine ganzen Bilder sortieren.\n",
                                  "[Sicherheits-Salamander]: Bevor du einen Ordner zum sortieren auswählst, könntest du hier eine Sicherungskopie erstellen."]
        return willkommensnachricht
        
    def destroy_window(self):

        if self.label_load1 is not None:
            self.label_load1.forget()

        if self.label_load is not None:
            self.label_load.forget()

        if self.label is not None:
            self.label.forget()

        if self.load_checkbox is not None:
            self.load_checkbox.forget()

        if self.continue_button is not None:
            self.continue_button.forget()

        if self.backup_checkbox is not None:
            self.backup_checkbox.forget()

        ma.done=True
    
def run_setup_window():
    setup_root = tk.Tk()
    setup_window = SetupWindow(setup_root)
    setup_root.mainloop()
        