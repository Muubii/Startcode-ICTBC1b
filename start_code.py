# import modulen
from pathlib import Path
import json
import pprint
from database_wrapper import Database

# parameters voor connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark")

# main

# Haal de eigenschappen op van een personeelslid
# altijd verbinding openen om query's uit te voeren
db.connect()

# pas deze query aan om het juiste personeelslid te selecteren
select_query = "SELECT * FROM personeelslid WHERE id = 2"
personeelslid = db.execute_query(select_query)

# altijd verbinding sluiten met de database als je klaar bent
db.close()

pprint.pp(personeelslid) # print de resultaten van de query op een overzichtelijke manier
print(personeelslid[0]['naam']) # voorbeeld van hoe je bij een eigenschap komt

# Haal alle onderhoudstaken op
# altijd verbinding openen om query's uit te voeren
db.connect()

leeftijd = int(personeelslid[0]['leeftijd'])

if leeftijd <= 24:
    max_fysieke_belasting = 25
elif leeftijd <= 50:
    max_fysieke_belasting = 40
else:
    max_fysieke_belasting = 20

if personeelslid[0]['verlaagde_fysieke_belasting']:
    max_fysieke_belasting = int(personeelslid[0]['verlaagde_fysieke_belasting'])

levels = ["Stagiair", "Junior", "Medior" ,"Senior"]

bevoegdheid_level = None

if personeelslid[0]['bevoegdheid'] in levels:
    bevoegdheid_level = levels.index(personeelslid[0]['bevoegdheid']) + 1

# Then build SQL query using max_fysieke_belasting
select_query = f"SELECT * FROM onderhoudstaak WHERE beroepstype = '{personeelslid[0]['beroepstype']}' AND fysieke_belasting <= '{max_fysieke_belasting}' AND ("

for i in range(bevoegdheid_level):
    select_query += f"bevoegdheid = '{levels[i]}'"
    if i < bevoegdheid_level -1:
        select_query += " OR "

select_query += ");"

onderhoudstaken = db.execute_query(select_query)
print(select_query)

# altijd verbinding sluiten met de database als je klaar bent
db.close()

# verzamel alle benodigde gegevens in een dictionary
dagtakenlijst = {
    # STAP 1: vul aan met andere benodigde eigenschappen
    "personeelsgegevens" : {
        "naam": personeelslid[0]['naam'],# voorbeeld van hoe je bij een eigenschap komt
        "werktijd": personeelslid[0]['werktijd'],
        "beroepstype": personeelslid[0]['beroepstype'],
        "bevoegdheid": personeelslid[0]['bevoegdheid'],
        "specialist_in_attracties": personeelslid[0]['specialist_in_attracties'],
        "pauze_opsplitsen": bool(personeelslid[0]['pauze_opsplitsen']),
        "leeftijd": personeelslid[0]['leeftijd'],
        "max_fysieke_belasting": max_fysieke_belasting,
    },
    "weergegevens" : {
        # STAP 4: vul aan met weergegevens
    }, 
    "dagtaken": [onderhoudstaken] # STAP 2: hier komt een lijst met alle dagtaken
    ,
    "totale_duur": 0 # STAP 3: aanpassen naar daadwerkelijke totale duur
}

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand, die kan worden ingelezen door de acceptatieomgeving
with open('dagtakenlijst_personeelslid_x.json', 'w') as json_bestand_uitvoer:
    json.dump(dagtakenlijst, json_bestand_uitvoer, indent=4)