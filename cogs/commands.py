import discord
from discord.ext import commands
bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)

class Test(commands.bot):
    def __init__(self, tree):
        self.tree = tree
    @tree.command(name="test", description="test command")
    async def test(self, interaction: discord.Interaction):
        return await interaction.response.send_message("test")


async def setup(bot: discord.commands.Bot) -> None:
    # finally, adding the cog to the bot
    await bot.add_cog(Test(bot=bot))