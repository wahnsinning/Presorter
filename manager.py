done=False
categories=[]
image_folder=""

#das hier ist nur um herauszufinden ob man schonmal kategorien in der kategorien csv 
#gespeichert hat.
#wenn ja, dann soll der willkommen zurück screen eingeleitet werden, weenn nicht 
#der neu hier? screen. es gibt bestimmt einen eleganteren weg herauszufinden ob
#man das programm schonmal geöffnet hat 

def count_letters_and_entries(arr):
    #leeres dictionary für buchstabenzähler
    letter_count = 0

    
    for word in arr:
        
        for letter in word:
            #zähle buchstaben im dictionary
            letter_count += 1

    #zähle die gesamtanzahl der einträge
    total_entries = len(arr)

    letter_count = letter_count+(total_entries*5.5)

    return letter_count