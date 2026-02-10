import json, pathlib
from modules.classes import *
from modules.data import *
DIR = pathlib.Path(__file__).parent.absolute()

with open(f"{DIR}/../data/default_server_config.json") as file:
    default_server_config = json.load(file)
with open(f"{DIR}/../data/default_user_config.json") as file:
    default_user_config = json.load(file)
with open(f"{DIR}/../data/config_config.json") as file:
    configs = json.load(file)

def server_updater(server: Server):
    cfg = server.config
    for k, v in configs.items():
        cfg[k] = cfg.get(k, v["default_value"])
    stats = server.stats
    for k, v in default_server_config["stats"].items():
        stats[k] = stats.get(k, v)

def user_updater(user: User):
    stats = user.stats
    for k, v in default_user_config["stats"].items():
        stats[k] = stats.get(k, v)

async def get_server_object(server_id):
    if server_id in servers.keys():
        return servers[server_id]
    await create_server_object(server_id)
    return servers[server_id]

async def get_user_object(user_id, user_name):
    if user_id in users.keys():
        return users[user_id]
    await create_user_object(user_id, user_name)
    return users[user_id]

async def create_server_object(server_id):
    servers[server_id] = Server(**default_server_config)
    server: Server = servers[server_id]
    server.id = server_id
    for config, value in configs.items():
        server.config[config] = value["default_value"]

async def create_user_object(user_id, user_name):
    users[user_id] = User(**default_user_config)
    user: User = users[user_id]
    user.id = user_id
    user.username = user_name