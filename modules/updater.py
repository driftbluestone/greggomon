import json, pathlib
from dataclasses import asdict, dataclass
DIR = pathlib.Path(__file__).parent.absolute()

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
    guess_counter: int
    words_found: list

@dataclass
class User:
    id: str
    username: str
    stats: dict

with open(f"{DIR}/../data/default_server_config.json") as file:
    default_server_config = json.load(file)
with open(f"{DIR}/../data/default_user_config.json") as file:
    default_user_config = json.load(file)

def server_updater(server: Server):
    cfg = server.config
    for k, v in default_server_config["config"].items():
        cfg[k] = cfg.get(k, v)
    stats = server.stats
    for k, v in default_server_config["stats"].items():
        stats[k] = stats.get(k, v)

def user_updater(user: User):
    stats = user.stats
    for k, v in default_user_config["stats"].items():
        stats[k] = stats.get(k, v)
    