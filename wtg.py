import discord, pathlib, json, time, random, typing
from dataclasses import asdict, dataclass
from modules import autocorrect, hints, updater, stats, config, permissions
from modules.classes import *
from modules.data import *

bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/TOKEN.txt", "r") as file:
    TOKEN = file.read()

#image sets aaahhhh
with open(f"{DIR}/gtceum.json", "r") as file:
    gtceum = json.load(file)

with open(f"{DIR}/data/default_server_config.json", "r") as file:
    default_server_config = json.load(file)
with open(f"{DIR}/data/default_user_config.json", "r") as file:
    default_user_config = json.load(file)

@bot.event
async def on_ready():
    # fix old answer buttons
    for server in servers.values():
        updater.server_updater(server)
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
    if servers[server_id].id != "": return servers[server_id]
    servers[server_id].id = server_id
    return servers[server_id]

async def get_user_object(user_id, user_name):
    users[user_id] = users.get(user_id, User(**default_user_config))
    if users[user_id].id != "": return users[user_id]
    users[user_id].id = user_id
    users[user_id].username = user_name
    return users[user_id]

async def save_user_state(user_id: str):
    with open(f"{DIR}/data/users/{user_id}.json", "w") as file:
        json.dump(asdict(users[user_id]), file)

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
    server: Server
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
    if new: stats.increment_server_stats(server, 0 , ["image_sent"], global_stats)
    await save_server_state(server_id)

@tree.command(name="answer",description="Submit a guess on the current image")
async def image(interaction:discord.Interaction, guess: str):
    await answer_logic(interaction, guess)

async def answer_logic(interaction: discord.Interaction, guess: str):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    server: Server
    server = await get_server_object(server_id)
    user = await get_user_object(str(interaction.user.id), interaction.user.name)

    # stat tracking variables
    increment_server = []
    increment_user = []

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
        increment_server.append("hint_sent")
        possible_hints = [x for x in server.answer_list if x not in server.words_found]
        if not possible_hints:
            hint = f"{server.config["guesses_to_hint"]} incorrect Guesses, huh? Heres a hint.\nAll of the words in the item name have been found already.\n"
        else:
            hint = f"{server.config["guesses_to_hint"]} incorrect Guesses, huh? Heres a hint.\nOne of the words in the item name is: '{random.choice(possible_hints)}'\n"
    user_guess = ""
    if (words_found == server.answer_list) and (answer_wrong == False):
        increment_server.append("correct_guess")
        increment_user.append("correct_guess")
        server.guess_counter = 0
        server.words_found = []
        server.guesses = {}
        stats.increment_server_stats(server, user, increment_server, global_stats)
        stats.increment_user_stats(server, user, increment_server, global_leaderboard)
        await send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True)
        return
    elif len(words_found) != 0 and server.config["show_correct_words_on_partial_correct"]:
        increment_server.append("incorrect_guess")
        increment_user.append("incorrect_guess")
        if not server.config["hide_user_guesses"]:
            user_guess = f"Your guess was: '{guess}'"
        await interaction.response.send_message(f"Not quite! Correct words: {words_found}\n{hint}{user_guess}", ephemeral=server.config["hide_user_guesses"])
    else:
        increment_server.append("incorrect_guess")
        increment_user.append("incorrect_guess")
        if not server.config["hide_user_guesses"]:
            user_guess = f"Your guess was: '{guess}'"
        await interaction.response.send_message(f"Nope!\n{hint}{user_guess}", ephemeral=server.config["hide_user_guesses"])
    server.guesses[user_id] += 1
    stats.increment_server_stats(server, user, increment_server, global_stats)
    stats.increment_user_stats(server, user, increment_server, global_leaderboard)
    await save_server_state(server_id)
    await save_user_state(user_id)

@tree.command(name="reveal",description="Reveals the answer, requires Global Scoreboard config disabled.")
async def reveal(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    server: Server
    server = await get_server_object(server_id)
    if server.config["global_scoreboard"]: return await interaction.response.send_message("Command disabled. Disable Global Scoreboard config to enable.", ephemeral=True)
    if await permissions.check_permission(interaction, server.admins): return await permissions.fail_permission_check(interaction)
    server.guesses = {}
    server.guess_counter = 0
    server.words_found = []
    await send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True)

@tree.command(name="leaderboard",description="shows leaderboard")
async def leaderboard(interaction:discord.Interaction, page: typing.Optional[int], user: typing.Optional[discord.User], server_leaderboard: typing.Optional[bool] = True):
    server: Server
    server = await get_server_object(str(interaction.guild_id))
    
    embed = stats.generate_leaderboard(page, server_leaderboard, user, users, server, global_leaderboard)
    await interaction.response.send_message(embed=embed)

@tree.command(name="statistics",description="Shows various statistics.")
async def statistics(interaction:discord.Interaction, user: typing.Optional[discord.User]):
    server: Server
    server = await get_server_object(str(interaction.guild_id))
    if user == None:
        user = interaction.user
    
    description = stats.generate_statspage(user, users, server, global_stats, global_leaderboard)
    description+= f"-# Ping: {round(bot.latency * 1000)} ms"
    embed = discord.Embed(description = description)
    await interaction.response.send_message(embed=embed)

@tree.command(name="config",description="Configures the bot. Without admin simply displays the server config.")
async def cfg(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    server = await get_server_object(server_id)
    embed = config.generate_config_table(server)
    if await permissions.check_permission(interaction, server.admins):
        await interaction.response.send_message(embed=embed) 
    else:
        view = config.Config_Button(server, interaction)
        await interaction.response.send_message(embed=embed, view=view) 

@tree.command(name="promote",description="Promote/Demote a user to/from Admin status.")
async def promote(interaction: discord.Interaction, user: discord.User):
    server_id = str(interaction.guild.id)
    server: Server = await get_server_object(server_id)
    # if await permissions.check_permission(interaction, server.admins): return await permissions.fail_permission_check(interaction)
    await permissions.promote(interaction, user, server)
    
    
    
bot.run(TOKEN)
