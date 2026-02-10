import json, pathlib, os
from dataclasses import asdict
from modules.classes import *
DIR = pathlib.Path(__file__).parent.absolute()

# data loading
servers = {}
users = {}
for img_path in os.listdir(f"{DIR}/../data/servers"):
    with open(f"{DIR}/../data/servers/{img_path}", "r") as file:
        servers[img_path[:-5]] = Server(**json.load(file))
for img_path in os.listdir(f"{DIR}/../data/users"):
    with open(f"{DIR}/../data/users/{img_path}", "r") as file:
        users[img_path[:-5]] = User(**json.load(file))
global_stats = {}
global_leaderboard = {}
with open(f"{DIR}/../data/global/leaderboard.json", "r") as file:
    global_leaderboard = json.load(file)
with open(f"{DIR}/../data/global/stats.json", "r") as file:
    global_stats = json.load(file)

async def save_server_state(server_id: str, save_global: bool = False):
    with open(f"{DIR}/../data/servers/{server_id}.json", "w") as file:
        json.dump(asdict(servers[server_id]), file)
    if save_global:
        with open(f"{DIR}/../data/global/leaderboard.json", "w") as file:
            json.dump(global_leaderboard, file)
        with open(f"{DIR}/../data/global/stats.json", "w") as file:
            json.dump(global_stats, file)

async def save_user_state(user_id: str):
    with open(f"{DIR}/../data/users/{user_id}.json", "w") as file:
        json.dump(asdict(users[user_id]), file)