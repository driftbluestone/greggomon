import discord, pathlib, json, time, random, typing
from discord.ext import commands
from modules import autocorrect, hints, updater, stats, config, permissions, image_logic, answer_input
from modules.answer_logic import answer_logic
from modules.updater import get_server_object, get_user_object
from modules.classes import *
from modules.data import *

#bot = discord.Client(intents=discord.Intents.all())
class GTTBOT(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=",",
            intents=discord.Intents.all()
        )

    async def setup_hook(self):
        await self.load_extension("cogs.commands")
bot = GTTBOT()
tree = bot.tree
#tree = discord.app_commands.CommandTree(bot)
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/TOKEN.txt", "r") as file:
    TOKEN = file.read()

@bot.event
async def on_ready():
    # await load_test()
    # fix old answer buttons and update server classes if needed
    for server in servers.values():
        updater.server_updater(server)
        if not server.embed == 0:
            channel = bot.get_channel(server.channel)
            message = await channel.fetch_message(server.embed)
            await message.edit(view=answer_input.answer_button(server, bot))
        await save_server_state(server.id)    
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as exception:
        print(f"Error syncing commands: {exception}")
    print(f'Gregging it up as {bot.user}!')

async def load_test():
    await bot.load_extension("cogs.commands")
@tree.command(name="image",description="Resends the previous image")
async def image(interaction:discord.Interaction):
    await image_logic.send_image(interaction, "", False, bot)

@tree.command(name="answer",description="Submit a guess on the current image")
async def image(interaction:discord.Interaction, guess: str):
    await answer_logic(interaction, guess, bot)

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
    await image_logic.send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True)

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
