import discord
from discord.ext import commands
from modules import initialization

# Bot class from @wabwit
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=",",
            intents=discord.Intents.all()
        )
    async def setup_hook(self):
        await self.load_extension("cogs.commands")
bot = Bot()

@bot.event
async def on_ready():
    await initialization.on_ready(bot)
    
bot.run(initialization.TOKEN)

