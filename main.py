from modules import initialization
bot = initialization.Bot()
@bot.event
async def on_ready():
    await initialization.on_ready(bot)
bot.run(initialization.TOKEN)
