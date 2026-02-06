from dataclasses import dataclass

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
    leaderboard: dict
    guess_counter: int
    words_found: list
    guesses: dict

@dataclass
class User:
    id: str
    username: str
    stats: dict

def increment_server_stats(server: Server, user: User, to_increment: list):
    for i in to_increment:
        if i == "correct_guess": server.leaderboard[user.id] = server.leaderboard.get(user.id, 0)+1
        else: server.stats[i]+=1

def increment_user_stats(user: User, to_increment: list):
    for i in to_increment:
        user.stats[i]+=1