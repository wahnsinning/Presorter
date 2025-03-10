import tkinter as tk
import csv

class Fenster:
    def __init__(self, master, eintraege):
        self.master = master
        self.eintraege = eintraege
        self.int_vars = [tk.IntVar() for _ in eintraege]
        self.create_widgets()

    def create_widgets(self):
        for i, (eintrag, var) in enumerate(zip(self.eintraege, self.int_vars)):
            checkbox = tk.Checkbutton(self.master, text=eintrag, variable=var)
            #setze den haken bei allen
            var.set(1)
            checkbox.grid(row=i, column=0, sticky="w")

        ok_button = tk.Button(self.master, text="Speichern", command=self.ok_button_clicked)
        ok_button.grid()

    def ok_button_clicked(self):
        ausgewaehlte_eintraege = [eintrag for eintrag, var in zip(self.eintraege, self.int_vars) if var.get()]
        print("Ausgewählte Einträge:", ausgewaehlte_eintraege)

        # Schreibe die ausgewählten Einträge in eine CSV-Datei
        self.write_to_csv(ausgewaehlte_eintraege, "Kategorien.csv")

        self.master.destroy()

        self.master.destroy()
    
    def write_to_csv(self,data, filename):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

def read_from_csv(filename):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        lines = list(reader)
        return lines


# # Testcode
# if __name__ == "__main__":
#     eintraege = ["Eintrag 1", "Eintrag 2", "Eintrag 3"]

#     root = tk.Tk()
#     fenster = Fenster(root, eintraege)
#     root.mainloop()