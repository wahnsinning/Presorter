#geschrieben von Silas Sinning in 2023
#zum ersten Mal mit KI-Ünterstützung (ChatGPT-3)


import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog,messagebox,PhotoImage
from PIL import Image, ImageTk
import ttkbootstrap as ttkb
import threading
import csv
import time
import ctypes


#eigene importe
import save_cat as sc
import setup as su
import manager as ma  
import einsortieren as es
import duplicate_detection as dd


def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True

    # Starten Sie das aktuelle Skript mit Administratorrechten neu
    script = sys.argv[0]
    params = ' '.join(sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, params, 1)


if run_as_admin():
    print("Das Skript wird mit Administratorrechten ausgeführt.")
    
    if getattr(sys, 'frozen', False):
        # Wenn das Skript in einer EXE-Datei gepackt ist
        application_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.chdir(application_path)

        print(application_path)

    else:
        # Wenn das Skript normal ausgeführt wird
        application_path = os.path.dirname(os.path.abspath(__file__))
    
        print(application_path)

    csv_file_path = os.path.join(application_path, 'Kategorien.csv')

    # Check if the file exists
    if not os.path.exists(csv_file_path):
        # If it doesn't exist, create the file
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

        
    class Presorter:

        def __init__(self, root, theme=None):
            self.root = root
            self.root.title("Bildsortierung")
            self.image_folder = None

            #this is for knowing when the setup is done to start building the window
            self.setup_done = threading.Event()
            self.buttons = []
            #set up fullscreen mode
            self.root.attributes('-fullscreen', True)
            self.root.bind("<Escape>", self.toggle_fullscreen)
            self.root.bind("<Return>", lambda event=None: self.add_new_category())
            #self.root.bind("<Right>", lambda event=None: self.skip_image())
            self.root.bind("<Left>", lambda event=None: self.undo_last_action())
            self.root.bind("<Control-r>", lambda event=None: self.rotate_image())
        
        
        def build_window(self, theme):
            
            self.image_files = []
            self.current_index = 0

            self.action_history = []

            self.last_used_category = None
            

            self.cutoff = []
            
            if not ma.categories:
                print("Keine Kategorien geladen. Voreinstellungsliste wird geladen.")
                self.categories = ["Sonstiges","Screenshots","Landschaften","Dokumente","Memes"]
            else:
                
                if ma.count_letters_and_entries(ma.categories)>130:

                    #alles vor dem cutoff
                    while ma.count_letters_and_entries(ma.categories)>130:
                        self.cutoff.append(ma.categories[-1])
                        ma.categories.pop()
                    self.categories = ma.categories

                    
                    messagebox.showwarning("Achtung", "Die Kategorienliste ist zu lang und wurde gekürzt.")
                    
                else:
                    self.categories = ma.categories
            #für die buttons in der untersten reihe
            self.start_categories = len(self.categories)
            self.button_x=0
            self.button_y=0

            #für die neuen buttons
            self.row=0
            self.col=0
            self.button_sum=0
            self.rowcount=0
            
            #style objekt
            self.style = ttkb.Style(theme=theme)


            #OUTER frame 
            self.outer = ttk.Frame(self.root, borderwidth=2, relief='solid')
            self.outer.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


            #frame for upper buttons
            self.button_frame_upper = ttkb.Frame(self.outer,borderwidth=2, relief='solid')
            self.button_frame_upper.pack(side=tk.TOP,fill=tk.X, pady=(10,0))
            

            #MIDDLE frame
            self.middle = ttk.Frame(self.outer)
            self.middle.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            root.update()

            #outer frame for progress bar 
            self.frame_prog_outer = ttkb.Frame(self.middle)
            self.frame_prog_outer.pack(side=tk.LEFT,fill=tk.Y, pady=(0,0), padx=(0,10))

            

            #inner frame for progress bar 
            self.frame_prog = ttkb.Frame(self.frame_prog_outer,borderwidth=2, relief='solid')
            self.frame_prog.pack(side=tk.TOP, pady=(0,0), padx=(0,0), anchor="w")
            
            #outer frame for picture name 
            self.frame_name_outer = ttkb.Frame(self.frame_prog_outer)
            self.frame_name_outer.pack(pady=0, side=tk.TOP, anchor="w")

            #label for image
            self.label = ttkb.Label(self.middle, text="", style="TLabel")
            self.label.place(x=self.root.winfo_screenwidth()/2,y=self.middle.winfo_height()/2.5,anchor="center")
            #self.label.pack(side=tk.LEFT,fill=tk.BOTH, expand=True, padx=(int(self.root.winfo_screenwidth()/2),0), pady=10)


            #frame for buttons
            self.button_frame = ttkb.Frame(self.outer,borderwidth=2, relief='solid')
            self.button_frame.pack(side=tk.BOTTOM,fill=tk.X, pady=(0,10))


            #outer frame for additional buttons 
            self.button_frame_add_outer = ttkb.Frame(self.middle)
            self.button_frame_add_outer.pack(side=tk.RIGHT,fill=tk.Y, pady=(0,0), padx=(0,0))


            #frame for additional buttons 
            self.button_frame_add = ttkb.Frame(self.button_frame_add_outer,borderwidth=2, relief='solid')
            self.button_frame_add.pack(side=tk.TOP, pady=(0,0), padx=(0,0), anchor="e")

        
            #frame for NEW buttons
            self.button_frame_new = ttkb.Frame(self.outer,borderwidth=2, relief='solid')
            self.button_frame_new.pack(side=tk.TOP, pady=0, fill=tk.X)

            # Frame für Thumbnail-Anzeigen
            self.thumbnail_frame_left = ttkb.Frame(self.frame_prog_outer, borderwidth=0, relief='solid')
            self.thumbnail_frame_left.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 10))

            self.thumbnail_frame_right = ttkb.Frame(self.button_frame_add_outer, borderwidth=0, relief='solid')
            self.thumbnail_frame_right.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 10))

            #liste für die linken thumbnails
            self.thumbnail_labels_left = []  
            for _ in range(3):  
                label = ttkb.Label(self.thumbnail_frame_left, image=None)
                label.pack(side=tk.LEFT, padx=5, pady=5)
                self.thumbnail_labels_left.append(label)

            #liste für die rechten thumbnails
            self.thumbnail_labels_right = []
            for _ in range(3):
                label = ttkb.Label(self.thumbnail_frame_right, image=None)
                label.pack(side=tk.LEFT, padx=5, pady=5)
                self.thumbnail_labels_right.append(label)

        
            #create buttons dynamically out of categories
            for index, category in enumerate(self.categories):
                #padx_value = (0, 5) if index == 0 else 5
                button = ttkb.Button(self.button_frame, text=category, command=lambda cat=category: self.label_image(cat))
                self.buttons.append(button)
                button.pack(side=tk.LEFT, padx=5)


            self.update_thumbnails_right()

            root.update()#damit die buttons existieren bevor ich die breite abfrage

            self.label_width = self.button_frame.winfo_width()  #actually frame with
            
            esc_button = ttkb.Button(self.button_frame_upper, text="ESC", command=self.toggle_fullscreen)
            esc_button.pack(side=tk.LEFT, padx=(0, 0), pady=(0,0))

            x_button = ttkb.Button(self.button_frame_upper, 
                                text="X", command=self.destroy_window, 
                                style="Warning.TButton")
            
            x_button.pack(side=tk.RIGHT)

            # Create a label for the progress bar
            progress_label = ttkb.Label(self.frame_prog, text="Fortschritt:", style="TLabel")
            progress_label.pack(pady=0)


            # Create a progress bar variable
            self.progress_var = tk.IntVar()
            self.progress_var.set(50)

            #self.progress_bar_.update()

            # Create a progress bar widget
            self.progress_bar = ttk.Progressbar(self.frame_prog, variable=self.progress_var, mode="determinate", length=self.button_frame_add.winfo_width(),style="success.Horizontal.TProgressbar")
            self.progress_bar.pack(pady=10)

            self.frame_name_outer = ttk.Label(self.frame_name_outer, text= "NAME DES BILDES" ) #### ist ja klar was hier hin soll xD
            self.frame_name_outer.pack(pady=10)

            #button to create folders 
            add_category_button = ttkb.Button(self.button_frame_add, 
                                            text="In Ordner sortieren", 
                                            command= lambda: es.sortiere_bilder(self.image_folder) ,
                                            style="Warning.TButton")
            add_category_button.pack(side=tk.TOP,padx=5,pady=5)

            #button to reset categories 
            add_category_button = ttkb.Button(self.button_frame_add, 
                                            text="Alle Ordner entpacken", 
                                            command= lambda: es.reverse(self.image_folder) ,
                                            style="Warning.TButton")
            add_category_button.pack(side=tk.TOP,padx=5,pady=5)

            #button to unpack folders 
            add_category_button = ttkb.Button(self.button_frame_add, 
                                            text="Dateinamen zurücksetzen", 
                                            command= lambda: es.kategorisierung_entfernen(self.image_folder) ,
                                            style="Warning Button")
            add_category_button.pack(side=tk.TOP,padx=5,pady=5)

            #button to check for duplicates
            add_duplicate_button = ttkb.Button(self.button_frame_add, 
                                            text="Duplikatprüfung", 
                                            command= lambda: dd.run_duplicate_check_gui(self.image_folder) ,
                                            style="Warning Button")
            add_duplicate_button.pack(side=tk.TOP,padx=5,pady=5)

            #button to save categories to csv
            add_category_button = ttkb.Button(self.button_frame, 
                                            text="Kategorien speichern", 
                                            command= self.write_categories_to_csv ,
                                            style="Warning.TButton")
            add_category_button.pack(side=tk.RIGHT,padx=5)
            
            #button to add a new category
            add_category_button = ttkb.Button(self.button_frame, 
                                            text="Kategorie hinzufügen (Enter)", 
                                            command=self.add_new_category)
            add_category_button.pack(side=tk.RIGHT, padx=5)

            self.new_category_entry = ttkb.Entry(self.button_frame)
            self.new_category_entry.pack(side=tk.RIGHT, padx=5)
            self.new_category_entry.config(state="normal")
            self.new_category_entry.focus_set()

            self.button_x = self.button_frame.winfo_rootx()
            self.button_y = self.button_frame.winfo_rooty()


            rotate_image_icon = PhotoImage(file="icons/rotate.png")  
            return_image_icon = PhotoImage(file="icons/return.png")
            skip_image_icon = PhotoImage(file="icons/skip.png")
            
            rotate_button = ttkb.Button(self.frame_prog_outer, padding=0,image=rotate_image_icon, command=self.rotate_image, style="Info.TButton")
            rotate_button.image = rotate_image_icon  # Speichern Sie eine Referenz auf das Bild, um Garbage Collection zu verhindern
            rotate_button.pack(side=tk.TOP, padx=5, pady=(5,5), anchor="w")

            rotate_label = ttkb.Label(self.frame_prog_outer, text="Bild drehen \n(Strg + R)", style="TLabel")
            rotate_label.pack(pady=0, side=tk.TOP, anchor="w")

            return_button = ttkb.Button(self.frame_prog_outer,padding=0, image=return_image_icon, command=self.undo_last_action, style="Info.TButton")
            return_button.image = return_image_icon  # Speichern Sie eine Referenz auf das Bild, um Garbage Collection zu verhindern
            return_button.pack(side=tk.TOP, padx=5, pady=(20,5), anchor="w")

            return_label = ttkb.Label(self.frame_prog_outer, text="Vorheriges Bild \n(Pfeiltaste links)", style="TLabel")
            return_label.pack(pady=0, side=tk.TOP, anchor="w")

            #skip_button = ttkb.Button(self.frame_prog_outer,padding=0, image=skip_image_icon, command=self.skip_image, style="Info.TButton")
            #skip_button.image = skip_image_icon  #Referenz auf das Bild speichern
            #skip_button.pack(side=tk.TOP, padx=5, pady=(20,5), anchor="w")

            #skip_label = ttkb.Label(self.frame_prog_outer, text="Bild überspringen \n(Pfeiltaste rechts)", style="TLabel")
            #skip_label.pack(pady=0, side=tk.TOP, anchor="w")
            #dieser button macht irgendwie die bilderanzeige der rechten seite kaputt und ist 
            #sowieso nicht besonders hilfreich


        def update_thumbnails_right(self):
            # Berechne den Startindex für die nächsten drei Bilder
            start_index = self.current_index + 1  # Beginne mit dem nächsten Bild
            end_index = min(len(self.image_files), start_index + 3)  # Füge drei Bilder hinzu, limitiere auf die Gesamtanzahl

            for i, label in enumerate(self.thumbnail_labels_right):
                label_index = start_index + i
                if label_index < end_index:
                    # Es gibt ein Bild, das angezeigt werden kann
                    image_file_name = self.image_files[label_index]
                    image_path = os.path.join(self.image_folder, image_file_name)
                    try:
                        image = Image.open(image_path)
                        thumbnail_size = (100, 100)
                        image.thumbnail(thumbnail_size)
                        photo = ImageTk.PhotoImage(image)
                        label.config(image=photo)
                        label.image = photo  # Speichere die Referenz, um Garbage Collection zu verhindern
                    except FileNotFoundError:
                        print(f"Datei nicht gefunden: {image_path}")
                else:
                    # Es gibt kein Bild für dieses Label, setze es zurück
                    label.config(image=None)
                    label.image = None  # Entferne die Referenz, um Garbage Collection zu ermöglichen


        def update_thumbnails_left(self):
            start_index = max(0, self.current_index - 3)
            end_index = max(0, self.current_index)  # Ende ist exklusiv

            for i, label in enumerate(self.thumbnail_labels_left):
                label_index = start_index + i
                if label_index < end_index:
                    image_file_name = self.last_used_category + "_" + self.image_files[label_index]
                    image_path = os.path.join(self.image_folder, image_file_name)
                    try:
                        image = Image.open(image_path)
                        thumbnail_size = (100, 100)
                        image.thumbnail(thumbnail_size)
                        photo = ImageTk.PhotoImage(image)
                        label.config(image=photo)
                        label.image = photo  # GC Maßnahme
                    except FileNotFoundError:
                        print(f"Datei nicht gefunden: {image_path}")
                else:
                    # wenn nicht genug bilder, setze die restlichen Labels zurück
                    label.config(image=None)
                    label.image = None  # Entferne die Referenz, um Garbage Collection zu ermöglichen

        
        def undo_last_action(self):
            if self.action_history:
                # Hole die letzte Aktion
                old_path, new_path = self.action_history.pop()

                # Benenne die Datei zurück
                os.rename(new_path, old_path)

                # Aktualisiere den Index und die Bildanzeige
                self.current_index = max(0, self.current_index - 1)
                self.show_image()
                self.update_thumbnails_left()
                self.update_thumbnails_right()
            else:
                messagebox.showinfo("¯\_(ツ)_/¯", "Weiter zurück geht nicht")

        def skip_image(self):
            # Überprüft, ob noch Bilder vorhanden sind
            if self.current_index < len(self.image_files) - 1:
                # Erhöht den Index um 1, um zum nächsten Bild zu springen
                self.current_index += 1
                # Zeigt das nächste Bild an
                self.show_image()
                
                self.update_thumbnails_left()
                self.update_thumbnails_right()

                # Update the Progressbar based on the current index and total number of images
                progress_percentage = int((self.current_index / len(self.image_files)) * 100)
                self.progress_var.set(progress_percentage)
            else:
                # Wenn es keine weiteren Bilder gibt, zeige eine Nachricht an
                messagebox.showinfo("Information", "Keine weiteren Bilder zum Anzeigen.")
            

    
        def destroy_window(self):
            self.root.destroy()

        def toggle_fullscreen(self, event=None):
            #zwischen fullscreen und normal wechseln
            state = not self.root.attributes('-fullscreen')
            self.root.attributes('-fullscreen', state)
                
        def load_images(self):
            self.image_folder = filedialog.askdirectory(title="Wähle einen Ordner mit Bildern")
            if self.image_folder:
                self.image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                self.show_image()

        def show_image(self):
            if self.current_index < len(self.image_files):
                image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
                image = Image.open(image_path)

                max_display_size = 400
                width, height = image.size
                aspect_ratio = width / height

                if width > height:
                    new_width = max_display_size
                    new_height = int(max_display_size / aspect_ratio)
                else:
                    new_height = max_display_size
                    new_width = int(max_display_size * aspect_ratio)

                image = image.resize((new_width, new_height))
                photo = ImageTk.PhotoImage(image)

                self.label.config(image=photo)
                self.label.image = photo

                # Aktualisiere den Namen des Bildes
                image_name = os.path.basename(image_path)  # Holt nur den Dateinamen
                self.update_image_name(image_name)

                # Update the Progressbar based on the current index and total number of images
                progress_percentage = int((self.current_index / len(self.image_files)) * 100)
                self.progress_var.set(progress_percentage)

        def update_image_name(self, image_name):
            self.frame_name_outer.config(text=image_name)

        def label_image(self, category):
            if self.current_index < len(self.image_files):
                old_path = os.path.join(self.image_folder, self.image_files[self.current_index])
                new_filename = f"{category}_{self.image_files[self.current_index]}"
                new_path = os.path.join(self.image_folder, new_filename)
                os.rename(old_path, new_path)


                # Speichere die Aktion in der Historie
                self.action_history.append((old_path, new_path))

                # Speichert die zuletzt verwendete Kategorie
                self.last_used_category = category

                self.current_index += 1
                self.show_image()
                self.update_thumbnails_left()  # Aktualisiert die Thumbnails
                self.update_thumbnails_right()

                # Update the Progressbar based on the current index and total number of images
                progress_percentage = int((self.current_index / len(self.image_files)) * 100)
                self.progress_var.set(progress_percentage)

            else:
                self.label.config(image=None)
                messagebox.showinfo("Erste Sahne", "Bada-bap-boom,POW. Alle Bilder sortiert.")
        
        
        def add_new_category(self):
            new_category = self.new_category_entry.get().strip()

            if new_category and new_category not in self.categories:
                # Create a new button for the added category
                button = ttkb.Button(self.button_frame_new, text=new_category,
                                    command=lambda cat=new_category: self.label_image(cat))
                self.buttons.append(button)

                # Calculate new button frame width
                self.button_frame_new.update()

                self.button_sum += button.winfo_reqwidth()


                if self.button_sum > root.winfo_screenwidth()-(root.winfo_screenwidth()*0.08):
                    
                    self.button_sum = 0
                    self.rowcount+=1

                    self.button_frame_new = ttkb.Frame(self.outer,borderwidth=2, relief='solid')
                    self.button_frame_new.pack(fill=tk.BOTH, padx=0, pady=0, side=tk.TOP)
                    
                    # Pack the button
                    button.pack(side=tk.LEFT, padx=5, pady=5)

                else:
                    # Pack the button
                    button.pack(side=tk.LEFT, padx=5, pady=5)

                # Clear the entry field and update the category list                                                                                        #hallo mo, peri oder pit :) (verstecktes moin und fröhliches coden)
                self.new_category_entry.delete(0, tk.END)
                self.categories.append(new_category)

                if self.rowcount>2:
                    messagebox.showinfo("Samma", "Jetzt reichts aber")
            else:
                messagebox.showerror("Döspaddel", "Leere oder doppelte Knöpfe, das wär Murks. Wo kämen wir denn da hin?")
            

        def rotate_image(self):
            if self.current_index < len(self.image_files):
                image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
                try:
                    image = Image.open(image_path)
                    rotated_image = image.rotate(-90, expand=True)#rotiert um 90 Grad g.d.U
                    rotated_image.save(image_path)  #überschreiben

                    #aktualisiere die Bildanzeige
                    self.show_image()
                except FileNotFoundError:
                    print(f"Datei nicht gefunden: {image_path}")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Beim Drehen des Bildes ist ein Fehler aufgetreten: {e}")


        def add_new_category_cutoff(self):
                
            new_category = self.cutoff[-1]

            if new_category and new_category not in self.categories:
                # Create a new button for the added category
                button = ttkb.Button(self.button_frame_new, text=new_category,
                                    command=lambda cat=new_category: self.label_image(cat))
                self.buttons.append(button)

                # Calculate new button frame width
                self.button_frame_new.update()

                self.button_sum += button.winfo_reqwidth()


                if self.button_sum > root.winfo_screenwidth()-(root.winfo_screenwidth()*0.08):
                    
                    self.button_sum = 0
                    self.rowcount+=1

                    self.button_frame_new = ttkb.Frame(self.outer,borderwidth=2, relief='solid')
                    self.button_frame_new.pack(fill=tk.BOTH, padx=0, pady=0, side=tk.TOP)
                    
                    # Pack the button
                    button.pack(side=tk.LEFT, padx=5, pady=5)

                else:
                    # Pack the button
                    button.pack(side=tk.LEFT, padx=5, pady=5)

                # Clear the entry field and update the category list
                self.new_category_entry.delete(0, tk.END)
                self.categories.append(new_category)

                if self.rowcount>2:
                    messagebox.showinfo("Samma", "Jetzt reichts aber")


        def write_categories_to_csv(self):
            categories = self.categories

            Dialog=tk.Frame(root,bd=2, relief='solid')
            Dialog.place(x=self.button_frame.winfo_width(),y=self.button_y, anchor="se")

            self.fenster = sc.Fenster(Dialog, categories)

            Dialog.update()

        

    def wait_for_image_folder_and_backup():
        while app.image_folder == None:
            time.sleep(1)
        
        if app.image_folder != None :

            #mach ein backup
            if es.backup_folder(app.image_folder) != False:

                messagebox.showinfo("Prima", "Sicherheitskopie erstellt")
            else:
                messagebox.showwarning("Achtung", "Es scheint, als wäre eine Sicherheitskopie bereits vorhanden.\nEs wird keine weitere erstellt.")

            
    def post_setup():

        #wenn setup fertig ist
        if ma.done:
            
            #wenn backup angeklickt wurde
            if setup_window.check_backup():
                
                #warte bis der image folder ausgewählt wurde und mach dann ein backup
                thread = threading.Thread(target=wait_for_image_folder_and_backup)
                thread.start()

            #lade die kategorien aus der csv
            if setup_window.check_load():
                ma.categories = sc.read_from_csv(csv_file_path)
                print
                print(csv_file_path)
                print(ma.categories)
                ma.categories =ma.categories[-1]
                

            app.build_window(theme='solar')
            
            app.load_images()
            app.update_thumbnails_right()
            app.progress_bar.configure(length=app.button_frame_add.winfo_width())


            #alles nach dem cutoff
            while len(app.cutoff)>0:
                app.add_new_category_cutoff()
                app.cutoff.pop()
            return
        
        root.after(2, post_setup)

else:
    print("Das Skript wird ohne Administratorrechte ausgeführt.")

if __name__ == "__main__":

    #grundlegendes fenster
    root = tk.Tk()
    root.geometry("600x600")

    #fenster für setup
    setup_window = su.SetupWindow(root, theme='solar')
    
    #in separatem thread warten bis setup fertig ist
    threading.Thread(target= post_setup,daemon=True).start()

    #das eigentliche fenster
    app = Presorter(root, theme='solar')

    root.mainloop()