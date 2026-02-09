from dataclasses import dataclass
import discord, math
from modules.classes import *

def increment_server_stats(server: Server, user: User, to_increment: list, stats):
    for i in to_increment:
        if i == "correct_guess": server.leaderboard[user.id] = server.leaderboard.get(user.id, 0)+1
        else: server.stats[i]+=1
        if server.config["global_scoreboard"]:
            stats[i]+=1

def increment_user_stats(server: Server, user: User, to_increment: list, leaderboard):
    for i in to_increment:
        user.stats[i]+=1
        if server.config["global_scoreboard"] and i == "correct_guess":
            leaderboard[user.id] = leaderboard.get(user.id, 0)+1
        

def generate_leaderboard(page: int, server: bool, user, users, srv: Server, global_leaderboard):
    if page == None: page = 1
    if server == None or server == True:
        data = srv.leaderboard
        option = "Server"
    else:
        data = global_leaderboard
        option = "global"
    if server: use_at = srv.config["at_user_in_server_leaderboard"]
    else: use_at = False
    if len(data) == 0: return discord.Embed(description="No leaderboard to display.")
    length = int(math.ceil(len(data)/10))
    if page > length or page < 1: return discord.Embed(description=f"Page out of bounds! Must be between 1 and {length}")

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

tracked_stats = {"correct_guess":"Correct Guesses", "incorrect_guess":"Incorrect Guesses", "image_sent":"Images Sent", "image_skipped":"Images Skipped", "hint_sent":"Hints sent"}
def generate_statspage(user_object, users, server, global_stats, global_leaderboard):
    description="### Global Stats\n"
    for k in global_stats.keys():
        description+=f"{tracked_stats[k]}: {global_stats[k]}\n"
    if str(user_object.id) in users:
        user = users[str(user_object.id)]
        description+=f"User Correct Guesses: {global_leaderboard[user.id]}\n"
    description+="### Server Stats\n"
    for k in server.stats.keys():
        description+=f"{tracked_stats[k]}: {server.stats[k]}\n"
    if str(user_object.id) in users:
        description+=f"User Correct Guesses: {server.leaderboard[user.id]}\n"
    if server.config["at_user_in_server_leaderboard"]:
        description+=f"### <@{user_object.id}> Stats\n"
    else:
        description+=f"### {user_object.name} Stats"
    if str(user_object.id) in users:
        for k in user.stats.keys():
            description+=f"{tracked_stats[k]}: {user.stats[k]}\n"
    else:
        description+="No data for user.\n"
    return description
