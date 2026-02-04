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

with open(f"{DIR}/../data/default_server_config.json") as file:
    default_config = json.load(file)
default_config = default_config["config"]

def server_updater(server: Server):
    cfg = server.config
    for k, v in default_config.items():
        cfg[k] = cfg.get(k, v)
    