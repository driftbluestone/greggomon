import json, cleaner

DIR = "C:/wtg-testing"

#HintList Initializer
HINTLIST = {}
with open(f"{DIR}/hintlist.json", "r") as file:
    HINTLIST = json.load(file)

#Cleans the hintlist entries to be the same as answers
for hint in HINTLIST:
    CleanedHints = []
    for item in HINTLIST[hint][1]:
        CleanedHints.append(cleaner.cleanInput(item))
    HINTLIST[hint][1] = CleanedHints

#Main Hint Checker
def HintChecker(answer):
    PossibleHints = []
    for hint in HINTLIST:
        if answer in HINTLIST[hint][1]:
            PossibleHints.append(HINTLIST[hint][0])
        else:
            PossibleHints.append("false")
    return PossibleHints # returns an array of possible hints, or false in the first entry if theres no available hints
