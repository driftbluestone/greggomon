import discord, pathlib, os, shutil, json, time, random, autocorrect, pickle
from dataclasses import asdict, dataclass
bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/TOKEN.txt", "r") as file:
    TOKEN = file.read()
with open(f"{DIR}/gtceum.json", "r") as file:
    gtceum = json.load(file)

# configs to eventually outsource to json
max_guess_length = 75

with open(f"{DIR}/data/default_server_config.json", "r") as file:
    default_server_config = json.load(file)

# data storage objects
@dataclass
class Server:
    id:str
    config:dict
    image_link:str
    answer:str
    answer_list:list
    embed:int
    channel: int
    stats:dict

@dataclass
class user:
    pass

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
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as exception:
        print(f"Error syncing commands: {exception}")
    print(f'Gregging it up as {bot.user}!')
    for server in servers.values():
        if not server.embed == 0:
            channel = bot.get_channel(server.channel)
            message = await channel.fetch_message(server.embed)
            await message.edit(view=answer_button())

async def get_server_object(server_id):
    servers[server_id] = servers.get(server_id, Server(**default_server_config))
    servers[server_id].id = server_id
    return servers[server_id]

async def save_server_state(server_id):
    with open(f"{DIR}/data/servers/{server_id}.json", "w") as file:
        json.dump(asdict(servers[server_id]), file)

# discord interaction buttons
class answer_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=1000000000)
    @discord.ui.button(label="Submit a Guess!", style=discord.ButtonStyle.primary, custom_id="open_modal_button")
    async def open_modal_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(answer_input())

class answer_input(discord.ui.Modal, title="Submit a Guess"):
    my_input = discord.ui.TextInput(
        label="Enter your guess:",
        placeholder="",
        style=discord.TextStyle.short, # discord.TextStyle.paragraph for multi line
        required=True,
        max_length=max_guess_length
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.my_input.value
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
    if not server.embed == 0: await (await interaction.channel.fetch_message(server.embed)).edit(view=None)
    msg = await interaction.response.send_message(content,embed=embed,view=answer_button())
    server.embed = msg.message_id
    server.channel = interaction.channel.id
    await save_server_state(server_id)

@tree.command(name="answer",description="Submit a guess on the current image")
async def image(interaction:discord.Interaction, guess: str):
    await answer_logic(interaction, guess)

async def answer_logic(interaction: discord.Interaction, guess: str):
    server_id = str(interaction.guild.id)
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
    if (words_found == server.answer_list) and (answer_wrong == False):
        await send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True)
        return
    elif len(words_found) == 0:
        await interaction.response.send_message(f"Nope!")
    else:
        await interaction.response.send_message(f"Not quite! Correct words: {words_found}")

bot.run(TOKEN)
