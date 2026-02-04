# Written with help from @wabwit on discord. Thanks!
import json, pathlib
DIR = f"{pathlib.Path(__file__).parent.absolute()}"
REPLACES=[0]*3
UPPER = {}
def load_data():
    global REPLACES, UPPER
    with open(f"{DIR}/../data/autocorrect.json", "r") as file:
        AUTOCORRECT = json.load(file)
        REPLACES = AUTOCORRECT["autocorrect"]
        UPPER = AUTOCORRECT["uppercase"]
load_data()

def correct_input(text):
    text = text.lower()
    for k, v in REPLACES.items():
        text = text.replace(k, v)
    return text

def uppercase(text):
    for k, v in UPPER.items():
        text = text.replace(k, v)
    return text

