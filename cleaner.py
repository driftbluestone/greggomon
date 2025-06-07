import json
DIR = "C:/wtg-testing"

#Init data
REPLACES = {}
UPPER = {}

#Loaders
def _loadData():
    global REPLACES, UPPER

    with open(f"{DIR}/replaces.json", "r") as file:
        REPLACES = json.load(file)
    with open(f"{DIR}/upper.json", "r") as file:
        UPPER = json.load(file)

def cleanInput(text):
    cleaned = text
    for k, v in REPLACES.items():
        cleaned = text.replace(k, v)
    cleaned = cleaned.replace("gtceum_","").replace(".png","").replace("_"," ")
    return cleaned

def uppervolt(text):
    for k, v in UPPER.items():
        text = text.replace(k, v)
    return text