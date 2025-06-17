# Mostly written by @wabwit on discord. Thanks!
import json, pathlib
DIR = pathlib.Path(__file__).parent.absolute()
REPLACES=[0]*3
UPPER = {}
def load_data():
    global REPLACES, UPPER
    with open(f"{DIR}/data/autocorrect.json", "r") as file:
        AUTOCORRECT = json.load(file)
        for i in range(3):
            REPLACES[i] = AUTOCORRECT[f"level_{i}"]
        UPPER = AUTOCORRECT["uppercase"]
load_data()

def correct_input(text, level):
    for i in range(level+1):
        for k, v in REPLACES[i].items():
            text = text.replace(k, v)
    return text

def uppercase(text):
    for k, v in UPPER.items():
        text = text.replace(k, v)
    return text

