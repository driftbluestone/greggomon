from dataclasses import dataclass
import discord, math

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

def generate_leaderboard(page: int, server: bool, user, users, srv: Server):
    if page == None:
        page = 1

    if server == None or server == True:
        data = srv.leaderboard
    else:
        data = "" # change this later aaaaah
    if server:
        use_at = srv.config["at_user_in_server_leaderboard"]
    else:
        use_at = False
    if server:
        option = "Server"
    else:
        option = "Global"
    
    if len(data) == 0:
        return discord.Embed(description="No leaderboard to display.")

    length = int(math.ceil(len(data)/10))
    if page > length or page < 1:
        return discord.Embed(description=f"Page out of bounds! Must be between 1 and {length}")

    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    if user != None:
        usrs = []
        for k, _ in sorted_data:
            usrs.append(k)
        if str(user.id) not in usrs:
            return discord.Embed(description="User has not played the game before.")
        ind = usrs.index(str(user.id))
        page = (math.floor(ind/10))+1
    sorted_data = sorted_data[((page-1)*10):((page)*10-1)]
    description = ""
    for i in range(len(sorted_data)):
        if use_at:
            description +=f"{i+(page*10)-9}. <@{sorted_data[i][0]}>: {sorted_data[i][1]}\n"
        else:
            description +=f"{i+(page*10)-9}. {users[sorted_data[i][0]].username}: {sorted_data[i][1]}\n"
    return discord.Embed(description=f"## {option} Leaderboard\n### Page {page} of {length}\n{description}")