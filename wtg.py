# CONFIG
TOKEN = ""
DIR ="C:/wtg-testing"

import discord # type: ignore
import random
import asyncio
import shutil
import json
import typing
import math
from discord.ext import commands # type: ignore 
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

REPLACES = {}
UPPER = {}
USER_SCORE= {}
ALLOWEDUSERS = []
ALLOWEDROLES = []
QUITLIST = []
IMAGESET = []
user_attempts = {}

def load_data():
    global REPLACES, UPPER, QUITLIST, IMAGESET, USER_SCORE, ALLOWEDUSERS, ALLOWEDROLES
    with open(f"{DIR}/replaces.json", "r") as file:
        REPLACES = json.load(file)
    with open(f"{DIR}/upper.json", "r") as file:
        UPPER = json.load(file)
    with open(f"{DIR}/quitlist.txt", "r") as file:
        QUITLIST = [line.strip() for line in file]
    with open(f"{DIR}/imagelist.txt", "r") as file:
        IMAGESET = [line.strip() for line in file]
    with open(f"{DIR}/userscore.json", "r") as file:
        USER_SCORE = json.load(file)
    with open(f"{DIR}/allowedusers.txt", "r") as file:
        ALLOWEDUSERS = [line.strip() for line in file]
    with open(f"{DIR}/allowedroles.txt", "r") as file:
        ALLOWEDROLES = [line.strip() for line in file]
load_data()

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    print(f'Time to greg, {bot.user}')

def cleanInput(text):
    for k, v in REPLACES.items():
        text = text.replace(k, v)
    return text

def uppervolt(text):
    for k, v in UPPER.items():
        text = text.replace(k, v)
    return text

async def sendImage(target, msgCont):
    global image, item, itemAnswerList, totalGuesses, user_attempts
    totalGuesses = 0

    user_attempts = {}

    item = random.choice(IMAGESET)
    image = f"{DIR}/imagelist/{item}"
    print(image)
    rimage = shutil.copyfile(f"{DIR}/imagelist/{item}",f"{DIR}/item.png")

    item = cleanInput(item)
    item = item.replace("gtceum_","").replace(".png","").replace("_"," ")
    itemAnswerList=item.split()

    file = discord.File(rimage) 

    if target.response.is_done(): 
        await target.followup.send(msgCont, file=file)
    else:
        await target.response.send_message(msgCont, file=file)

@bot.command("quit")
async def quit_bot(ctx):
    print(ctx.author.roles)
    print(ctx.author.id)
    if (str(ctx.author.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, ctx.author.roles)):
        await ctx.reply("o7")
        await quit()
    else:
        await ctx.reply(random.choice(QUITLIST))

async def processMessage(source, content_lower, user_id):
    global totalGuesses, answerFoundList, user_attempts
    content_lower = cleanInput(content_lower)
    response_method = source.followup.send
    responseList = content_lower.split()
    answerFoundList = []
    answerWrong = 0
    totalGuesses+=1
    for word in responseList:
        if word in itemAnswerList:
            answerFoundList.append(word)
        else:
            answerWrong = 1

    itemAnswerList.sort()
    answerFoundList.sort()

    if answerFoundList == itemAnswerList and answerWrong != 1:
        await sendImage(source, f"'{uppervolt(item.title())}' is correct!\nMoving onto the next image...")
        if user_id not in USER_SCORE:
           USER_SCORE[user_id] = 0
        USER_SCORE[user_id]+=1
        with open(f"{DIR}/userscore.json", "w") as file:
            json.dump(USER_SCORE, file)
        user_attempts = {}
    else:
        if user_id not in user_attempts:
            user_attempts[user_id] = 0

        if not answerFoundList:
            user_attempts[user_id] += 1
            if totalGuesses >= 10:
                await hint_message_slash(source)
            else:
                await response_method("Nope!")
        else:
            user_attempts[user_id] += 1
            GuessLeftStatement = ""
            match(user_attempts[user_id]):
                case 2:
                    GuessLeftStatement = " You have one guess left."
                case 3:
                    GuessLeftStatement = " You're out of guesses."
                case _:
                    GuessLeftStatent = ""
            await response_method(f"Not Quite!{GuessLeftStatement} Correct words: {answerFoundList}")

    await asyncio.to_thread(print, user_attempts)

async def hint_message_slash(interaction: discord.Interaction):
    possible_hints = [x for x in itemAnswerList if x not in answerFoundList]
    if not possible_hints:
        await interaction.followup.send("10 incorrect Guesses, huh? Heres a hint.\nAll of the words in the item name have been found already.", ephemeral=False)
        return
    await interaction.followup.send(f"10 incorrect Guesses, huh? Heres a hint.\nOne of the words in the item name is: {random.choice(possible_hints)}")

@bot.tree.command(name="image", description="Sends a new image.")
async def image(interaction: discord.Interaction):
    if (str(interaction.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, interaction.user.roles)):
        await interaction.response.defer()
        await sendImage(interaction, "")
    else:
        await interaction.response.send_message("Permission denied.", ephemeral=True)
    return

@bot.tree.command(name="answer", description="Lets you answer")
async def answer_1(interaction: discord.Interaction, answer: str,):
    await answer_r(interaction, answer)

@bot.tree.command(name="a", description="Lets you answer")
async def answer_2(interaction: discord.Interaction, answer: str,):
    await answer_r(interaction, answer)

async def answer_r(interaction, user_input):
    global user_attempts
    await interaction.response.defer(ephemeral=False)
    user_id = str(interaction.user.id)
    content_lower = user_input.lower()

    if user_attempts.get(user_id, 0) < 3:
        await processMessage(interaction, content_lower, user_id)
    else:
        await interaction.followup.send("You've used all your guesses!")

@bot.tree.command(name="reset", description="**Admin Only.** Reset guesses and hints for user.")
async def resetGuesses(ctx: discord.Interaction):
    global user_attempts
    if (str(ctx.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, ctx.user.roles)):
        user_attempts.pop(str(ctx.user.id), None)
        await ctx.response.send_message(f"{ctx.user.mention}, Guesses and hits reset.", ephemeral=True)
    else:
        await ctx.response.send_message("Permission denied.", ephemeral=True)
        return

@bot.tree.command(name="reveal", description="**Admin Only.** Reveals the name of the latest image")
async def reveal(interaction: discord.Interaction):
    if (str(interaction.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, interaction.user.roles)):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(f"The answer was:\n{uppervolt(item.title())}")
        await sendImage(interaction, "")
    else:
        await interaction.response.send_message("Permission denied.", ephemeral=True)
    return

@bot.tree.command(name="reload", description="**Admin Only.** Reloads important dictionaries and lists.")
async def reload(interaction: discord.Interaction):
    if (str(interaction.user.id) in ALLOWEDUSERS) or (discord.utils.find(lambda r: str(r.id) in ALLOWEDROLES, interaction.user.roles)):
        load_data()
        await interaction.response.send_message(f"Dictionaries and lists reloaded!")
    else:
        await interaction.response.send_message("Permission denied.", ephemeral=True)
    return

@bot.tree.command(name="score", description="Shows the top scores, can select pages.")
async def scorepg(interaction: discord.Interaction, page: typing.Optional[int]):
    global USER_SCORE, klist, vlist
    if not page:
        page = 1
    if page > int(math.ceil((len(USER_SCORE)/10))) or page < 1:
        await interaction.response.send_message(f"Invalid page! Must be between 1 and {int(math.ceil((len(USER_SCORE)/10)))}.")
    else:
        user_id = str(interaction.user)
        if user_id not in USER_SCORE:
               USER_SCORE[user_id] = 0
        klist = []
        vlist = []
        sorted_user_score = sorted(USER_SCORE.items(), key=lambda x: x[1], reverse=True)
        for k, v in sorted_user_score:
            klist.append(k)
            vlist.append(v)

        descbuilder = ""
        for i in range(10):
            pos2=i+(10*(page-1))
            try:
                descbuilder=descbuilder+(f"{str(pos2)}. <@{int(klist[pos2])}>: {vlist[pos2]}\n")
            except: pass

        embed = discord.Embed(title=f"Page {page} of {int(math.ceil((len(USER_SCORE)/10)))}", description=descbuilder)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userscore", description="Shows a specific user's score.")
async def userscore(interaction: discord.Interaction, user: typing.Optional[discord.User]):
    global klist, vlist
    
    if user == None:
        user = interaction.user
    user_id = str(user.id)
    if user_id not in USER_SCORE:
           USER_SCORE[user_id] = 0
    klist = []
    vlist = []
    sorted_user_score = sorted(USER_SCORE.items(), key=lambda x: x[1], reverse=True)
    for k, v in sorted_user_score:
        klist.append(k)
        vlist.append(v)

    descbuilder = ""
    pos=klist.index(user_id)
    for i in range(10):
        pos2 = pos+i-5
        if pos2<0: pass
        else:
            try:
                descbuilder=descbuilder+(f"{str(pos2)}. <@{int(klist[pos2])}>: {vlist[pos2]}\n")
            except: pass
        i+=1
    embed = discord.Embed(title=f"{user.name}'s score", color=0x222222, description=descbuilder)

    await interaction.response.send_message(embed=embed)
    
bot.run(TOKEN)
