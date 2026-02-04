import discord, pathlib, os, shutil, json, time, random
from dataclasses import asdict, dataclass
from modules import autocorrect, hints, config
bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/TOKEN.txt", "r") as file:
    TOKEN = file.read()

with open(f"{DIR}/gtceum.json", "r") as file:
    gtceum = json.load(file)

# configs to eventually outsource to json


with open(f"{DIR}/data/default_server_config.json", "r") as file:
    default_server_config = json.load(file)

# data storage objects
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
    guesses: dict

@dataclass
class user:
    id: str
    stats: dict

@dataclass
class image_set:
    pass

# data loading
servers = {}
for img_path in os.listdir(f"{DIR}/data/servers"):
    with open(f"{DIR}/data/servers/{img_path}", "r") as file:
        servers[img_path[:-5]] = Server(**json.load(file))

@bot.event
async def on_ready():
    # fix old answer buttons
    for server in servers.values():
        config.server_updater(server)
        if not server.embed == 0:
            channel = bot.get_channel(server.channel)
            message = await channel.fetch_message(server.embed)
            await message.edit(view=answer_button(server))
        await save_server_state(server.id)    
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as exception:
        print(f"Error syncing commands: {exception}")
    print(f'Gregging it up as {bot.user}!')

async def get_server_object(server_id):
    servers[server_id] = servers.get(server_id, Server(**default_server_config))
    servers[server_id].id = server_id
    return servers[server_id]

async def save_server_state(server_id: str):
    with open(f"{DIR}/data/servers/{server_id}.json", "w") as file:
        json.dump(asdict(servers[server_id]), file)

# discord interaction buttons
class answer_button(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=1000000000)
        self.server: Server
        self.server = server
    @discord.ui.button(label="Submit a Guess!", style=discord.ButtonStyle.primary, custom_id="open_modal_button")
    async def open_modal_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(answer_input(self.server))

class answer_input(discord.ui.Modal, title="Submit a Guess"):
    def __init__(self, server):
        super().__init__()
        self.server: Server
        self.server = server
        self.user_input = discord.ui.TextInput(
            label="Enter your guess:",
            placeholder="",
            style=discord.TextStyle.short, # discord.TextStyle.paragraph for multi line
            required=True,
            max_length=self.server.config["max_guess_length"]
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.user_input.value
        await answer_logic(interaction, user_input)

@tree.command(name="image",description="Resends the previous image")
async def image(interaction:discord.Interaction):
    await send_image(interaction, "", False)

async def send_image(interaction: discord.Interaction, content: str, new: bool):
    server_id = str(interaction.guild.id)
    server = await get_server_object(server_id)
    if server.answer == "": new = True
    if new:
        server.answer, server.image_link = random.choice(list(gtceum.items()))
        server.answer_list = autocorrect.correct_input(server.answer).split("_")
        server.answer = server.answer.replace("_", " ").title()
    print(server.answer)
    embed=discord.Embed()
    embed.set_image(url=server.image_link)
    if not server.embed == 0:
        channel = bot.get_channel(server.channel)
        message = await channel.fetch_message(server.embed)
        await message.edit(view=None)
    msg = await interaction.response.send_message(content,embed=embed,view=answer_button(server))
    server.embed = msg.message_id
    server.channel = interaction.channel.id
    await save_server_state(server_id)

@tree.command(name="answer",description="Submit a guess on the current image")
async def image(interaction:discord.Interaction, guess: str):
    await answer_logic(interaction, guess)

async def answer_logic(interaction: discord.Interaction, guess: str):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    server: Server
    server = await get_server_object(server_id)
    guess_list = autocorrect.correct_input(guess).split()
    words_found = []
    answer_wrong = False
    for item in guess_list:
        if item in server.answer_list:
            words_found.append(item)
        else:
            answer_wrong = True
    words_found.sort()
    server.answer_list.sort()

    server.guesses[user_id] = server.guesses.get(user_id, 0)
    if server.guesses[user_id] == server.config["user_guess_limit"]:
        return await interaction.response.send_message("You're out of guesses!")
    # hint logic. Eventually move to seperate python file!
    server.guess_counter+=1
    server.words_found.extend(words_found)
    hint = hints.get_hint(server)
    if server.guess_counter == server.config["guesses_to_hint"]:
        possible_hints = [x for x in server.answer_list if x not in server.words_found]
        if not possible_hints:
            hint = f"{server.config["guesses_to_hint"]} incorrect Guesses, huh? Heres a hint.\nAll of the words in the item name have been found already."
        else:
            hint = f"{server.config["guesses_to_hint"]} incorrect Guesses, huh? Heres a hint.\nOne of the words in the item name is: '{random.choice(possible_hints)}'"
    if (words_found == server.answer_list) and (answer_wrong == False):
        server.guess_counter = 0
        server.words_found = []
        server.guesses = {}
        await send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True)
        return
    elif len(words_found) == 0:
        await interaction.response.send_message(f"Nope!\n{hint}")
    else:
        await interaction.response.send_message(f"Not quite! Correct words: {words_found}\n{hint}")
    server.guesses[user_id] += 1
    await save_server_state(server_id)

@tree.command(name="reveal",description="INCOMPLETE!! reveals the answer")
async def reveal(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    server: Server
    server = await get_server_object(server_id)
    await send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True)

@tree.command(name="config",description="Configures the bot")
async def cfg(interaction: discord.Interaction):
    pass
bot.run(TOKEN)
