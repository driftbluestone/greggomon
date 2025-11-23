# this program just upload every image in a folder to a discord channel
import discord, pathlib, os, shutil, json, time
from discord import app_commands
bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/TOKEN.txt", "r") as file:
    TOKEN = file.read()

set = input(">> ")

@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f'Gregging it up as {bot.user}!')
images = {}
@tree.command(name="imager",description="imager")
async def imager(interaction:discord.Interaction):
    time1 = int(time.time())
    interaction.response.defer
    count=0
    for img_path in os.listdir(f"{DIR}/imageset/{set}"):
        count+=1
        shutil.copyfile(f"{DIR}/imageset/{set}/{img_path}", f"{DIR}/item.png")
        message = await interaction.channel.send(f"{str(count)}" ,file=discord.File(f"{DIR}/item.png"))
        images[img_path] = str(message.attachments[0].url)
    with open(f"{DIR}/{set}.json", "w") as file:
        json.dump(images, file)
    time2 = int(time.time())
    print(f"Started at {time1}, ended at {time2}, total time: {time2-time1}s, or {(time2-time1)/60}m")
    
bot.run(TOKEN)
