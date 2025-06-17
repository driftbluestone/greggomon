# IMPORTS
import discord, random, shutil, json, typing, time, pathlib, os, math, autocorrect, hints
from discord import app_commands
# INITIALIZATION
bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)
DIR = pathlib.Path(__file__).parent.absolute()
complaints = [1381485837874626660, 1381488559848030238]
# Variable initializaton
image_time = {}
user_attempts = {}
total_guesses = {}
answer_key = {}
answer_list = {}
item = {}
item_corrected = {}
image_path = {}
copied_image = {}
last_feedback = {}
last_gbsb_change = {}
last_image = {}
found_words = {}
users_skipped = {}
quit = [0,0]
# Get bot token
with open(f"{DIR}/TOKEN.txt", "r") as file:
    TOKEN = file.read()

D = -5
# Load a bunch of important dictionaries and lists
def load_data():
    # Its multiple lines so line length isn't too long
    global SUPERADMINS, QUITLIST
    global SUBCOMMANDS, IMAGESET
    global CONFIG_VALUES, BANNED, CONFIG
    global STATISTICS
    CONFIG = {}
    STATISTICS = {"global":{},"server":{},"user":{}}
    with open(f"{DIR}/data/data.json", "r") as file:
        data =json.load(file)
        QUITLIST = data["quit"]
        SUPERADMINS = data["superadmins"]
    with open(f"{DIR}/data/subcommands.json", "r") as file:
        SUBCOMMANDS = json.load(file)
    with open(f"{DIR}/data/imagelist.json", "r") as file:
        IMAGESET = json.load(file)
    with open(f"{DIR}/data/config_values.json", "r") as file:
        CONFIG_VALUES = json.load(file)
    with open(f"{DIR}/data/banned.json", "r") as file:
        BANNED = json.load(file)
    for filepath in os.listdir(f"{DIR}/data/config"):
        with open(f"{DIR}/data/config/{filepath}", "r") as file:
            CONFIG[f"{filepath[:D]}"] = json.load(file)
    for filepath in os.listdir(f"{DIR}/data/scores"):
        for sfilepath in os.listdir(f"{DIR}/data/scores/{filepath}"):
            with open(f"{DIR}/data/scores/{filepath}/{sfilepath}", "r") as file:
                STATISTICS[filepath][sfilepath[:D]] = json.load(file)
load_data()

@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f'Gregging it up as {bot.user}!')

def check_channel(interaction: discord.Interaction, channel):
    server_id = str(interaction.guild_id)
    if CONFIG[server_id]["channels"][channel] != interaction.channel_id:
        return True
    return False

def check_permission(interaction: discord.Interaction):
    server_id = str(interaction.guild_id)
    if (str(interaction.user.id) in CONFIG[server_id]["permissions"][0]):
        return False
    if (discord.utils.find(lambda r: str(r.id) in CONFIG[server_id]["permissions"][1], interaction.user.roles)):
        return False
    return True

async def process_guess(interaction: discord.Interaction, content):
    global total_guesses, answer_key, answer_list, item, user_attempts
    server_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    words_found = []
    # Get answer into a usable state for answering logic
    response_list = (autocorrect.correct_input(f" {content} ", CONFIG[server_id]["Autocorrect Level"])).split()
    # make sure total_guesses[server_id] has a value
    total_guesses[server_id] +=1
    user_attempts[server_id][user_id] = (user_attempts[server_id].get(user_id, 0)) +1
    # This is where the magic happens
    answer_wrong = False
    for word in response_list:
        if word in answer_list[server_id]:
            words_found.append(word)
        else:
            answer_wrong = True
    words_found.sort()
    answer_list[server_id].sort()

    # hint logic
    hint = ""
    if total_guesses[server_id] >= CONFIG[server_id]["Guesses to Hint"]:
        possible_hints = [x for x in answer_list[server_id] if x not in found_words[server_id]]
        print(found_words[server_id])
        print(possible_hints)
        if not possible_hints:
            hint = f"{CONFIG[server_id]["Guesses to Hint"]} incorrect Guesses, huh? Heres a hint.\nAll of the words in the item name have been found already."
        else:
            hint = f"{CONFIG[server_id]["Guesses to Hint"]} incorrect Guesses, huh? Heres a hint.\nOne of the words in the item name is: '{random.choice(possible_hints)}'"

    # Warn the user when then have 1 and 0 guesses left
    guess_warning = ""
    if user_attempts[server_id][user_id] == CONFIG[server_id]["Guesses Per User"]-1:
        guess_warning = "You have one guess left.\n"
    elif user_attempts[server_id][user_id]== CONFIG[server_id]["Guesses Per User"]:
        guess_warning = "You've run out of guesses.\n"

    # Respond based on if they were correct, partially correct, or incorrect
    if (words_found == answer_list[server_id]) and (answer_wrong == False):
        item_title = autocorrect.uppercase(answer_key[server_id].title())
        await send_image(interaction, f"'{item_title}' is correct!\nMoving on the the next image...", True, True)
        return
    elif len(words_found) == 0:
        await interaction.response.send_message(f"Nope! {guess_warning}{hint}")
    else:
        found_words[server_id].extend(words_found)
        await interaction.response.send_message(f"Not quite! {guess_warning}Correct words: {words_found}\n{hint}")
    score_increment(interaction, ["incorrect_guess"])

# This function is seperated from the command because it is also called when the correct answer is guessed or when the skip command is used
async def send_image(interaction: discord.Interaction, message_content, new, increment_user_score):
    global answer_key, item, image_time, user_attempts, total_guesses, copied_image, answer_list
    server_id = str(interaction.guild_id)
    if new == True:
        # Reset any variables that are reset when a new image is sent
        user_attempts[server_id] = {}
        found_words[server_id] = []
        total_guesses[server_id] = 0
        users_skipped[server_id] = []

        item[server_id] = get_image(server_id)
        i = 0
        while any(keyword in item[server_id] for keyword in CONFIG[server_id]["banned_keywords"]) and i in range(20):
            item[server_id] = get_image(server_id)
            i+=1

        # Record time for the skip command
        image_time[server_id] = int(time.time())
        last_image[server_id] = int(time.time())
        print(f"New image for {server_id}")
        print(f"Time: {image_time[server_id]}")
        img_path = f"{DIR}/imageset/{item[server_id].split('_', 1)[0]}/{item[server_id]}"
        print(f"Path: {img_path}")
        # Copy the image to {DIR}/images/item_{server_id}.png, which overwrites the old image, and obscures the item name
        copied_image[server_id] = f"{DIR}/images/item_{server_id}.png"
        shutil.copyfile(f"{img_path}", copied_image[server_id])
        # List of every word in the item name for answering logic
        answer_key[server_id] = (autocorrect.correct_input(item[server_id], CONFIG[server_id]["Autocorrect Level"]))
        answer_list[server_id] = answer_key[server_id].split()
        if increment_user_score == False:
            score_increment(interaction, ["image"])
        else:
            score_increment(interaction, ["image", "correct_guess"])
        
    await interaction.response.send_message(message_content, file=discord.File(copied_image[server_id]))

def get_image(server_id):
    global CONFIG
    x=[]
    for i in CONFIG[server_id]["image_sets"]:
        x.extend(IMAGESET[i])
    return random.choice(x)

@tree.command(name="image", description="Resends the current image, or sends a new one if none exists.")
async def image(interaction:discord.Interaction):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if check_channel(interaction, 0): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channel"][0]}>", ephemeral=True)
    message_content = ""
    if copied_image.get(server_id, "") == "":
        new = True
    else:
        new = False
        if last_image[server_id]+60 >= time.time():
            await interaction.response.send_message(f"Command still on cooldown! Can be used again in {int(last_image[server_id]+60 - time.time())} seconds.", ephemeral=True)
            return

    await send_image(interaction, message_content, new, False)

@tree.command(name="info", description="Help and changelogs.")
async def info(interaction: discord.Interaction, sub: typing.Optional[str]):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if check_channel(interaction, 1): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channel"][1]}>", ephemeral=True)
    if sub==None:
        embed=discord.Embed(title="Available Subcommands", description=str(list(SUBCOMMANDS.keys())))
        await interaction.response.send_message(embed=embed)
        return
    sub=sub.lower()
    if sub not in SUBCOMMANDS.keys():
        await interaction.response.send_message("Invalid subcommand.", ephemeral=True)
        return
    if SUBCOMMANDS[sub].endswith(".txt"):
        with open(f"{DIR}/data/info/{sub}.txt", "r") as file:
            embed=discord.Embed(description=file.read())
    else:
        embed=discord.Embed(description=SUBCOMMANDS[sub])
    await interaction.response.send_message(embed=embed)

# Both commands just call answer_r, /a exists for convenience
@tree.command(name="answer", description="Lets you answer")
async def answer_1(interaction: discord.Interaction, answer: str,):
    await answer_r(interaction, answer)

@tree.command(name="a", description="Lets you answer")
async def answer_2(interaction: discord.Interaction, answer: str,):
    await answer_r(interaction, answer)

async def answer_r(interaction: discord.Interaction, user_input):
    setup(interaction)
    global user_attempts
    server_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    # Make sure they're running the command in the same channel the image is in
    if check_channel(interaction, 0): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channels"][0]}>", ephemeral=True)

    user_input = user_input.lower()
    if not user_attempts[server_id].get(user_id, 0) < CONFIG[server_id]["Guesses Per User"]:
        await interaction.response.send_message("You've used all your guesses!")
        return
    if len(user_input) > CONFIG[server_id]["Max Guess Length"]:
        await interaction.response.send_message(f"Guess is longer than max length of {CONFIG[server_id]["Max Guess Length"]} characters.")
    else:
        await process_guess(interaction, user_input)

@tree.command(name="skip", description="Skips the current image")
async def skip(interaction: discord.Interaction):
    server_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    if check_channel(interaction, 0): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channels"][0]}>", ephemeral=True)
    if image_time[server_id]+(CONFIG[server_id]["Time to Secondary Skip"]*60) <= int(time.time()):
        await send_image(interaction, f"The answer was:\n{autocorrect.uppercase(answer_key[server_id].title())}", True, False)
        return
    if not image_time[server_id]+(CONFIG[server_id]["Time to Skip"]*60) <= int(time.time()):
        await interaction.response.send_message(f"You have to wait {CONFIG[server_id]["Time to Skip"]} minutes before skipping.", ephemeral=True)
        return
    if user_id in users_skipped[server_id]:
        try_again_message = f"Try again in {int(CONFIG[server_id]["Time to Secondary Skip"]-(int((time.time()-image_time[server_id])/60)))} minutes"
        await interaction.response.send_message(f"You've already used /skip for this image. {try_again_message}", ephemeral=True)
        return
    if not user_attempts[server_id].get(user_id, 0) >= CONFIG[server_id]["Guesses Per User"]:
        await interaction.response.send_message(f"You must use all {CONFIG[server_id]["Guesses Per User"]} guesses before skipping.", ephemeral=True)
        return
    users_skipped[server_id].append(user_id)
    if not len(users_skipped[server_id]) >= CONFIG[server_id]["Users Required to Skip"]:
        await interaction.response.send_message(f"Skip processed. {len(users_skipped[server_id])}/{CONFIG[server_id]["Users Required to Skip"]}")
        return
    else:
        await send_image(interaction, f"The answer was:\n{autocorrect.uppercase(answer_key[server_id].title())}", True, False)

@tree.command(name="reveal", description="Admin Only. Requires Global Scoreboard config to be disabled. Reveals the name of the latest image.")
async def reveal(interaction: discord.Interaction):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if CONFIG[server_id]["Global Scoreboard"] == 1: return await interaction.response.send_message("This command is disabled, Global Scoreboard is enabled.", ephemeral=True)
    if check_channel(interaction, 0): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channel"][0]}>", ephemeral=True)
    if check_permission(interaction): return await interaction.response.send_message("Permission denied.", ephemeral=True)
    await send_image(interaction, f"The answer was:\n{autocorrect.uppercase(answer_key[server_id].title())}", True, False)

# SCOREBOARD SHENANIGANS
def score_increment(interaction: discord.Interaction, increment_type: list):
    server_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    username = interaction.user.name
    score_setup("user", user_id)
    score_setup("server", server_id)
    if CONFIG[server_id]["Global Scoreboard"] == 1:
        if "correct_guess" in increment_type:
            STATISTICS["global"]["servers"][server_id] = STATISTICS["global"]["servers"].get(server_id, 0)+1
            STATISTICS["global"]["users"][username] = STATISTICS["global"]["users"].get(username, 0)+1
            STATISTICS["global"]["stats"]["correct_guesses"]+=1
            STATISTICS["global"]["stats"]["total_guesses"]+=1
        if "incorrect_guess" in increment_type:
            STATISTICS["global"]["stats"]["total_guesses"]+=1
        if "image" in increment_type:
            STATISTICS["global"]["stats"]["images_sent"]+=1
        dump_scores(interaction, "global")
    if "correct_guess" in increment_type:
        STATISTICS["user"][user_id]["correct_guesses"]+=1
        STATISTICS["user"][user_id]["total_guesses"]+=1
        STATISTICS["server"][server_id]["stats"]["correct_guesses"]+=1
        STATISTICS["server"][server_id]["stats"]["total_guesses"]+=1
        STATISTICS["server"][server_id]["users"][user_id] = STATISTICS["server"][server_id]["users"].get(user_id, 0)+1
    if "incorrect_guess" in increment_type:
        STATISTICS["server"][server_id]["stats"]["total_guesses"]+=1
        STATISTICS["user"][user_id]["total_guesses"]+=1
    if "image" in increment_type:
        STATISTICS["server"][server_id]["stats"]["images_sent"]+=1
    dump_scores(interaction, "")

def dump_scores(interaction: discord.Interaction, dumptype):
    if dumptype != "global":
        server_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        with open(f"{DIR}/data/scores/server/{server_id}.json", "w") as file:
            json.dump(STATISTICS["server"][server_id], file)
        with open(f"{DIR}/data/scores/user/{user_id}.json", "w") as file:
            json.dump(STATISTICS["user"][user_id], file)
        return
    for filepath in os.listdir(f"{DIR}/data/scores/{dumptype}"):
        with open(f"{DIR}/data/scores/{dumptype}/{filepath}", "w") as file:
            json.dump(STATISTICS[dumptype][filepath[:D]], file)

def score_setup(type: str, type_id:str):
    filepath = f"{DIR}/data/scores/{type}/{type_id}.json"
    if not os.path.isfile(filepath):
        shutil.copyfile(f"{DIR}/data/{type}.json", filepath)
        with open(filepath,"r") as file:
            STATISTICS[type][type_id] = json.load(file)

# if you ever do servers leaderboard: {(bot.get_guild(int(ID GO HERE))).name}

@tree.command(name="stats", description="View statistics.")
async def stats(interaction: discord.Interaction, user: typing.Optional[discord.User]):
    if user != None and user.bot: return await interaction.response.send_message("Bots dont have stats!", ephemeral=True)
    if user != None: return await interaction.response.send_message(embed=discord.Embed(description=build_user_stats(interaction, user)))
    server_id = str(interaction.guild_id)
    descbuilder = f"## Statistics\n### Global\n"
    descbuilder+= f"- Correct Guesses: {STATISTICS["global"]["stats"]["correct_guesses"]}\n"
    descbuilder+= f"- Total Guesses:      {STATISTICS["global"]["stats"]["total_guesses"]}\n"
    descbuilder+= f"- Images Sent:         {STATISTICS["global"]["stats"]["images_sent"]}\n"
    descbuilder+= f"### Server\n"
    descbuilder+= f"- Correct Guesses: {STATISTICS["server"][server_id]["stats"]["correct_guesses"]}\n"
    descbuilder+= f"- Total Guesses:       {STATISTICS["server"][server_id]["stats"]["total_guesses"]}\n"
    descbuilder+= f"- Images Sent:          {STATISTICS["server"][server_id]["stats"]["images_sent"]}\n"
    descbuilder+=build_user_stats(interaction, interaction.user)
    descbuilder+= f"-# Ping: {round(bot.latency * 1000)} ms"
    await interaction.response.send_message(embed=discord.Embed(description=descbuilder))

spaces = "                       "
def build_user_stats(interaction: discord.Interaction, user: discord.User):
    user_id = str(user.id)
    username = user.name
    server_id = str(interaction.guild_id)
    if not os.path.isfile(f"{DIR}/data/scores/user/{user_id}.json"):
        return f"### {user.name}'s stats\n- Correct Guesses (Global): 0\n- Correct Guesses (Server): 0\n- Total Guesses:{spaces}0"
    descbuilder = f"### {user.name}'s stats\n"
    descbuilder+= f"- Correct Guesses (Global): {STATISTICS["global"]["users"].get(username, 0)}\n"
    descbuilder+= f"- Correct Guesses (Server): {STATISTICS["server"][server_id]["users"].get(user_id, 0)}\n"
    descbuilder+= f"- Total Guesses:{spaces}{STATISTICS["user"][user_id]["total_guesses"]}\n"
    return descbuilder

# leaderboards. too many leaderboards.
@tree.command(name="leaderboard", description="See top scores of servers and users.")
@app_commands.describe(option="Global or server leaderboard")
@app_commands.choices(
    option=[
        app_commands.Choice(name="Global", value="global"),
        app_commands.Choice(name="Server", value="server")
    ])
async def leaderboard(interaction: discord.Interaction, option: typing.Optional[app_commands.Choice[str]], user: typing.Optional[discord.User], page: typing.Optional[int]):
    if option == None: option = "server"
    else: option = option.value
    if user != None and user.bot: return await interaction.response.send_message("Bots dont have stats!", ephemeral=True)
    if user == None:
        max_page = int(math.ceil((len(STATISTICS["global"]["users"])/10)))
    if page != None:
        if page > max_page: return interaction.response.send_message(f"Invalid page! Must be between 1 and {max_page}.", ephemeral=True)
    if user == None and page == None: page = 1
    klist, vlist = [], []
    if option == "global":
        sorted_user_score = sorted(STATISTICS["global"]["users"].items(), key=lambda x: x[1], reverse=True)
    else:
        server_id = str(interaction.guild_id)
        sorted_user_score = sorted(STATISTICS["server"][server_id]["users"].items(), key=lambda x: x[1], reverse=True)
    for k, v in sorted_user_score:
        klist.append(k)
        vlist.append(v)
    descbuilder = ""
    if user == None: pos, is_user = page, False
    else: pos, is_user = klist.index(user.name), True
    for i in range(10):
        pos2=poscalc(i, pos, is_user)
        if pos2<0: continue
        try: descbuilder+=(f"{str(pos2+1)}. {get_user(option, klist[pos2])}: {vlist[pos2]}\n")
        except: pass
    if user == None: title_content = f"## {option.title()} Leaderboard\n### Page {page} of {max_page}"
    else: title_content = f"## {user.name}'s score\n**({option.title()})**"
    embed = discord.Embed(description=f"{title_content}\n{descbuilder}")
    await interaction.response.send_message(embed=embed)

def poscalc(i, p, is_user):
    if is_user:
        return p+i-5
    else:
        return i+(10*(p-1))

def get_user(option, pos):
    if option == "server":
        return f"<@{pos}>"
    else: return pos

# CONFIGURATION COMAMNDS
def setup(interaction: discord.Interaction):
    server_id = str(interaction.guild_id)
    filepath = f"{DIR}/data/config/{server_id}.json"
    if not os.path.isfile(filepath):
        shutil.copyfile(f"{DIR}/data/base.json", filepath)
        with open(f"{DIR}/data/config/{server_id}.json", "r") as file:
            CONFIG[server_id] = json.load(file)
        CONFIG[server_id]["channels"] = [interaction.channel_id]*2
        if str(interaction.user.id) in SUPERADMINS:
            CONFIG[server_id]["permissions"][0].append(str(interaction.user.id))
        with open(f"{DIR}/data/config/{server_id}.json", "w") as file:
            json.dump(CONFIG[server_id], file)

@tree.command(name="permission", description="Requires Administrator permission. Configures which users/roles can access admin commands.")
async def permission(interaction:discord.Interaction, role: typing.Optional[discord.Role], user: typing.Optional[discord.User]):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if role == None and user == None:
        if check_channel(interaction, 1): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channel"][1]}>", ephemeral=True)
        await interaction.response.send_message(embed=discord.Embed(title="Permissions",description=get_permissions(server_id)))
        return
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Insufficient permissions.", ephemeral=True)
        return
    elif role != None and user != None:
        await interaction.response.send_message("Please select only one.", ephemeral=True)
        return

    if user != None:
        if str(user.id) in CONFIG[server_id]["permissions"][0]:
            CONFIG[server_id]["permissions"][0].remove(str(user.id))
            update = f"Removed <@{str(user.id)}>"
        else:
            CONFIG[server_id]["permissions"][0].append(str(user.id))
            update = f"Added <@{str(user.id)}>"
    else:
        if str(role.id) in CONFIG[server_id]["permissions"][1]:
            CONFIG[server_id]["permissions"][1].remove(str(role.id))
            update = f"Removed <@&{str(role.id)}>"
        else:
            CONFIG[server_id]["permissions"][1].append(str(role.id))
            update = f"Added <@&{str(role.id)}>"
    with open(f"{DIR}/data/config/{server_id}.json", "w") as file:
        json.dump(CONFIG[server_id], file)
    await interaction.response.send_message(embed=discord.Embed(description=f"Permissions updated!\n{update}"))

def get_permissions(server_id):
    descbuilder = "**Users:**\n"
    for i in CONFIG[server_id]["permissions"][0]:
        descbuilder+=f"<@{i}>\n"
    descbuilder+="**Roles:**\n"
    for i in CONFIG[server_id]["permissions"][1]:
        descbuilder+=f"<@&{i}>\n"
    return descbuilder

@tree.command(name="config", description="Admin only. Configures the bot.")
@app_commands.describe(option="Select an image set to enable/disable")
@app_commands.choices(
    option=[
        app_commands.Choice(name="Autocorrect Level", value="Autocorrect Level"),
        app_commands.Choice(name="Global Scoreboard", value="Global Scoreboard"),
        app_commands.Choice(name="Guesses Per User", value="Guesses Per User"),
        app_commands.Choice(name="Guesses to Hint", value="Guesses to Hint"),
        app_commands.Choice(name="Users to Skip", value="Users to Skip"),
        app_commands.Choice(name="Time to Skip (Minutes)", value="Time to Skip"),
        app_commands.Choice(name="Time to Secondary Skip (Minutes)", value="Time to Secondary Skip"),
        app_commands.Choice(name="Max Guess Length", value="Max Guess Length")
    ])
async def config(interaction: discord.Interaction, option: typing.Optional[app_commands.Choice[str]], value: typing.Optional[int]):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if option == None:
        if check_channel(interaction, 1): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channel"][1]}>", ephemeral=True)
        await interaction.response.send_message(embed=discord.Embed(title="Settings", description=get_server_config(server_id)))
        return
    if check_permission(interaction): return await interaction.response.send_message("Permission denied.", ephemeral=True)
    if option.value == "Global Scoreboard":
        last_gbsb_change[server_id] = last_gbsb_change.get(server_id, 0)
        if last_gbsb_change[server_id]+3600 >= time.time():
            await interaction.response.send_message("You must wait one hour between toggling Global Scoreboard!", ephemeral=True)
            return
        else:
            last_gbsb_change[server_id] = int(time.time())
    if (value not in range(CONFIG_VALUES[option.value][0], CONFIG_VALUES[option.value][1]+1)) or value == None:
        await interaction.response.send_message(f"Value not in accepted range. Expected between {CONFIG_VALUES[option.value][0]}, {CONFIG_VALUES[option.value][1]}")
        return
    CONFIG[server_id][option.value] = value
    with open(f"{DIR}/data/config/{server_id}.json", "w") as file:
        json.dump(CONFIG[server_id], file)
    await interaction.response.send_message(f"{option.name} is now {value}.")
passlist = ["permissions", "channels", "image_sets", "banned_keywords"]
def get_server_config(server_id):
    descbuilder = ""
    for k, v in CONFIG[server_id].items():
        if k not in passlist:
            descbuilder+=f"{k}: {v}\n"
    return(descbuilder)

@tree.command(name="channel", description="Admin only. Sets the bot's active channels")
async def activechannel(interaction: discord.Interaction, primary: discord.TextChannel, secondary: discord.TextChannel):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if check_permission(interaction): return await interaction.response.send_message("Permission denied.", ephemeral=True)
    CONFIG[server_id]["channels"] = CONFIG[server_id].get("channels", [0,0])
    CONFIG[server_id]["channels"][0] = primary.id
    CONFIG[server_id]["channels"][1] = secondary.id
    with open(f"{DIR}/data/config/{server_id}.json", "w") as file:
        json.dump(CONFIG[server_id], file)
    print(f"New active channels in {server_id}: {CONFIG[server_id]["channels"]}")
    await interaction.response.send_message(embed=discord.Embed(description=f"Active channels updated.\nMain: <#{primary.id}>\nSecondary: <#{secondary.id}>"))

@app_commands.describe(set="Select an image set to enable/disable")
@app_commands.choices(
    set=[
        app_commands.Choice(name="Refreshed", value="refreshed"),
        app_commands.Choice(name="Classic", value="classic"),
        app_commands.Choice(name="Vanilla", value="vanilla")
    ])
@tree.command(name="image_set", description="Shows which image sets can be used by the bot, or selects which ones can be used.")
async def image_set(interaction: discord.Interaction, set: typing.Optional[app_commands.Choice[str]]):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if set == None:
        if check_channel(interaction, 1): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channel"][1]}>", ephemeral=True)
        descbuilder = ""
        for k in IMAGESET:
            descbuilder +=check_image_set(k, server_id)
        embed=discord.Embed(title="Image Sets", description=descbuilder)
        await interaction.response.send_message(embed=embed)
        return
    if check_permission(interaction): return await interaction.response.send_message("Permission denied.", ephemeral=True)
    if not set.value in CONFIG[server_id]["image_sets"]:
        CONFIG[server_id]["image_sets"].append(set.value)
        returnmessage = f"{set.name} images can now be used!"
    else:
        CONFIG[server_id]["image_sets"].remove(set.value)
        returnmessage = f"{set.name} images can no longer be used!"
    with open(f"{DIR}/data/config/{server_id}.json", "w") as file:
        json.dump(CONFIG[server_id], file)
    await interaction.response.send_message(returnmessage)

def check_image_set(k, server_id):
    if k in CONFIG[server_id]["image_sets"]:
        x=f"✅ {k}\n"
    else:
        x=f"<:no:1382514706295685160> {k}\n"
    return x

@tree.command(name="ban_keyword", description="Admin Only. Remove any keywords from appearing. Max 10.")
async def bankeyword(interaction: discord.Interaction, keyword: typing.Optional[str]):
    setup(interaction)
    server_id = str(interaction.guild_id)
    if keyword == None:
        if check_channel(interaction, 1): return await interaction.response.send_message(f"Wrong channel! <#{CONFIG[server_id]["channel"][1]}>", ephemeral=True)
        await interaction.response.send_message(f"Banned keywords:\n{CONFIG[server_id]["banned_keywords"]}")
        return
    if check_permission(interaction): return await interaction.response.send_message("Permission denied.", ephemeral=True)
    keyword.replace(" ","_")
    if len(keyword) <= 3:
        await interaction.response.send_message("Keyword is too short! Min 4 characters.")
    if keyword in CONFIG[server_id]["banned_keywords"]:
        CONFIG[server_id]["banned_keywords"].remove(keyword)
        await interaction.response.send_message(f"Removed keyword {keyword}!")
        return
    if len(CONFIG[server_id]["banned_keywords"]) >= 10:
        await interaction.response.send_message("Banned keyword list is too long! Max 10.", ephemeral=True)
        return
    CONFIG[server_id]["banned_keywords"].append(keyword)
    await interaction.response.send_message(f"Added keyword {keyword}!")
    with open(f"{DIR}/data/config/{server_id}.json", "w") as file:
        json.dump(CONFIG[server_id], file)

@tree.command(name="feedback", description="Submit suggestions or bugs.")
@app_commands.describe(feedback="Which kind of feedback?")
@app_commands.choices(
    feedback=[
        app_commands.Choice(name="Suggestion", value="suggestion"),
        app_commands.Choice(name="Bug", value="bug")
    ])
async def feedback(interaction: discord.Interaction, feedback: app_commands.Choice[str], text: str):
    if interaction.user.id in BANNED:
        await interaction.response.send_message("You have been banned from this command.", ephemeral=True)
        return
    user_id = interaction.user.id
    last_feedback[user_id] = last_feedback.get(user_id, 0)
    if last_feedback[user_id]+60 >= time.time():
        await interaction.response.send_message(f"Command still on cooldown! Can be used again in {int(last_feedback[user_id]+60 - time.time())} seconds.", ephemeral=True)
        return
    last_feedback[user_id]=int(time.time())
    if feedback.value == "suggestion":
        embed = discord.Embed(title=f"{interaction.user.name} suggests:", description=text)
        channel = bot.get_channel(complaints[0])
        sent_message = await channel.send(embed=embed)
        await sent_message.add_reaction('👍')
        await sent_message.add_reaction('👎')
        await interaction.response.send_message("Suggestion submitted!", ephemeral=True)
    elif feedback.value == "bug":
        channel = bot.get_channel(complaints[1])
        embed = discord.Embed(title=f"{interaction.user.name} reported a bug:", description=text)
        await channel.send(embed=embed)
        await interaction.response.send_message("Bug reported!", ephemeral=True)

@tree.command(name="reload", description="Super admin only. Reloads important dictionaries and lists.")
async def reload(interaction: discord.Interaction):
    if not((str(interaction.user.id) in SUPERADMINS)): return await interaction.response.send_message("Permission denied.",ephemeral=True)
    load_data()
    autocorrect.load_data()
    await interaction.response.send_message(f"Dictionaries and lists reloaded!")

@tree.command(name="feedbackban", description="Super admin only. Ban users from using the feedback command.")
async def feedbackban(interaction: discord.Interaction, user: discord.User):
    if not((str(interaction.user.id) in SUPERADMINS)): return await interaction.response.send_message("Permission denied.",ephemeral=True)
    if user.id in BANNED:
        BANNED.remove(user.id)
        returnmessage = f"Unbanned user <@{user.id}>"
    else:
        BANNED.append(user.id)
        returnmessage = f"Banned user <@{user.id}>"
    with open(f"{DIR}/data/banned.json", "w") as file:
        json.dump(BANNED, file)
    await interaction.response.send_message(embed=discord.Embed(description=returnmessage))

@tree.command(name="quit", description="Super admin only. Kills the bot.")
async def quit_bot(interaction: discord.Interaction):
    global quit
    print(interaction.user.id)
    print(interaction.user.name)
    if not((str(interaction.user.id) in SUPERADMINS)):
        await interaction.response.send_message(random.choice(QUITLIST))
        return
    if (not quit[0] == interaction.user.id) or (quit[1] + 60 <= time.time()):
        quit[0] = interaction.user.id
        quit[1] = int(time.time())
        await interaction.response.send_message("Are you sure? Run the command again within 1 minute to confirm.")
        return
    await interaction.response.send_message("o7")
    await bot.close()

bot.run(TOKEN)
# thanks for playing
# -drift ;3
