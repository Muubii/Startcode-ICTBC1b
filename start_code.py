# import modulen
from pathlib import Path
import json
import pprint
from database_wrapper import Database

# parameters voor connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark")

# main
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

#statement als de personeelslid leeftijd berekenen hoeveel fysieke belasting hij/zij moet dragen.
if leeftijd <= 24:
    max_fysieke_belasting = 25
elif leeftijd <= 50:
    max_fysieke_belasting = 40
else:
    max_fysieke_belasting = 20

# Controleert of het personeelslid een verlaagde fysieke belasting heeft
# en stelt de maximale fysieke belasting in op die waarde
if personeelslid[0]['verlaagde_fysieke_belasting']:
    max_fysieke_belasting = int(personeelslid[0]['verlaagde_fysieke_belasting'])

levels = ["Stagiair", "Junior", "Medior" ,"Senior"]

bevoegdheid_level = None

# Bepaalt het bevoegdheidsniveau van het personeelslid.
# Het gekozen level wordt naar een index vertaald (bijvoorbeeld: 'Stagiair' = 0),
# waarbij +1 wordt opgeteld zodat het niveau overeenkomt met het correcte bereik
if personeelslid[0]['bevoegdheid'] in levels:
    bevoegdheid_level = levels.index(personeelslid[0]['bevoegdheid']) + 1

# Bouwt de basis SQL-query.
# De query haalt onderhoudstaken op die passen bij het beroepstype van het personeelslid
# en waarvan de fysieke belasting lager of gelijk is aan de maximaal toegestane belasting
select_query = f"SELECT * FROM onderhoudstaak WHERE beroepstype = '{personeelslid[0]['beroepstype']}' AND fysieke_belasting <= '{max_fysieke_belasting}' AND ("

# Vult de WHERE-gedeelte aan met de toegestane bevoegdheidsniveaus.
# Bijvoorbeeld: als bevoegdheid 'Medior' is, worden ook 'Stagiair' en 'Junior' meegenomen
for i in range(bevoegdheid_level):
    select_query += f"bevoegdheid = '{levels[i]}'"
    if i < bevoegdheid_level -1:
        select_query += " OR "

select_query += ");"

onderhoudstaken = db.execute_query(select_query)
print(select_query) #print in terminal de query wat word ingevoegd

# altijd verbinding sluiten met de database als je klaar bent
db.close()

# Alle peprsoneelsgegevens in een json
dagtakenlijst = {
    "personeelsgegevens" : {
        "naam": personeelslid[0]['naam'],
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