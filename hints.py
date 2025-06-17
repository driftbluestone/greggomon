# Written with help from @wabwit and @digestlotion on discord. Thanks!
import json, pathlib, random, autocorrect
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/data/hints.json", "r") as file:
    HINTS = json.load(file)

# Cleans the hintlist entries to be the same as answers
for hint in HINTS:
    CleanedHints = []
    for item in HINTS[hint]:
        CleanedHints.append(autocorrect.correct_input(item, 1))
    HINTS[hint] = CleanedHints

# Main Hint Checker
def get_hint(item, all_words_found):
    possible_hints = []
    for k, hint in HINTS.items():
        if item in hint:
            possible_hints.append(k)
    if not len(possible_hints) == 0:
        return(f"This item is associated with {random.choice(possible_hints)}")
    return possible_hints # Returns an array of possible hints, or false in the first entry if theres no available hints
# print(get_hint("acidic enriched naquadah solution"), ["enriched", "acidic"])