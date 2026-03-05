import discord, typing
from discord import app_commands
from discord.ext import commands
from modules import autocorrect, stats, config, permissions, image_logic
from modules.answer_logic import answer_logic
from modules.updater import get_server_object
from modules.classes import *
from modules.data import *

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="answer",description="Submit a guess on the current image")
    async def answer(self, interaction:discord.Interaction, guess: str):
        await answer_logic(interaction, guess, self.bot)

    @app_commands.command(name="image",description="Resends the previous image")
    async def image(self, interaction: discord.Interaction):
        await image_logic.send_image(interaction, "", False, self.bot)

    @app_commands.command(name="reveal",description="Reveals the answer, requires Global Scoreboard config disabled.")
    async def reveal(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        server: Server
        server = await get_server_object(server_id)
        if server.config["global_scoreboard"]: return await interaction.response.send_message("Command disabled. Disable Global Scoreboard config to enable.", ephemeral=True)
        if await permissions.check_permission(interaction, server.admins): return await permissions.fail_permission_check(interaction)
        server.guesses = {}
        server.guess_counter = 0
        server.words_found = []
        await image_logic.send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True)

    @app_commands.command(name="leaderboard",description="shows leaderboard")
    async def leaderboard(self, interaction:discord.Interaction, page: typing.Optional[int], user: typing.Optional[discord.User], server_leaderboard: typing.Optional[bool] = True):
        server: Server
        server = await get_server_object(str(interaction.guild_id))
        
        embed = stats.generate_leaderboard(page, server_leaderboard, user, users, server, global_leaderboard)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="statistics",description="Shows various statistics.")
    async def statistics(self, interaction:discord.Interaction, user: typing.Optional[discord.User]):
        server: Server
        server = await get_server_object(str(interaction.guild_id))
        if user == None:
            user = interaction.user
        
        description = stats.generate_statspage(user, users, server, global_stats, global_leaderboard)
        description+= f"-# Ping: {round(self.bot.latency * 1000)} ms"
        embed = discord.Embed(description = description)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="config",description="Configures the bot. Without admin simply displays the server config.")
    async def cfg(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        server = await get_server_object(server_id)
        embed = config.generate_config_table(server)
        if await permissions.check_permission(interaction, server.admins):
            await interaction.response.send_message(embed=embed) 
        else:
            view = config.Config_Button(server, interaction)
            await interaction.response.send_message(embed=embed, view=view) 

    @app_commands.command(name="promote",description="Promote/Demote a user to/from Admin status.")
    async def promote(self, interaction: discord.Interaction, user: discord.User):
        server_id = str(interaction.guild.id)
        server: Server = await get_server_object(server_id)
        # if await permissions.check_permission(interaction, server.admins): return await permissions.fail_permission_check(interaction)
        await permissions.promote(interaction, user, server)


async def setup(bot: commands.Bot) -> None:
    # finally, adding the cog to the bot
    await bot.add_cog(Commands(bot=bot))