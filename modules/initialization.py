import pathlib
from modules import updater, answer_input, data
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/../TOKEN.txt", "r") as file:
    TOKEN = file.read()

async def on_ready(bot):
    # fix old answer buttons and update server classes if needed
    for server in data.servers.values():
        updater.server_updater(server)
        if not server.embed == 0:
            channel = bot.get_channel(server.channel)
            message = await channel.fetch_message(server.embed)
            await message.edit(view=answer_input.answer_button(server, bot))
        await data.save_server_state(server.id)    
    # sync all commands to discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as exception:
        print(f"Error syncing commands: {exception}")
    # bot is finally ready
    print(f'Gregging it up as {bot.user}!')