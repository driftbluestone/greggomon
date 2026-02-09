from dataclasses import dataclass
def test():
    pass
@dataclass
class Server:
    id: str
    config: dict
    image_link: str
    answer: str
    answer_list: list
    embed: int
    channel: int
    stats: dict
    admins: list
    leaderboard: dict
    guess_counter: int
    words_found: list
    guesses: dict

@dataclass
class User:
    id: str
    username: str
    stats: dict

@dataclass
class image_set:
    pass