import discord, random, pathlib, json
from modules import autocorrect, data, updater, stats, answer_input
from modules.classes import *
from modules.data import global_stats
DIR = pathlib.Path(__file__).parent.absolute()

#image sets aaahhhh
with open(f"{DIR}/../data/image_sets/gtceum.json", "r") as file:
    gtceum = json.load(file)

async def send_image(interaction: discord.Interaction, content: str, new: bool, bot):
    server_id = str(interaction.guild.id)
    server: Server
    server = await updater.get_server_object(server_id)
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
    msg = await interaction.response.send_message(content,embed=embed,view=answer_input.answer_button(server, bot))
    server.embed = msg.message_id
    server.channel = interaction.channel.id
    if new: stats.increment_server_stats(server, 0 , ["image_sent"], global_stats)
    await data.save_server_state(server_id, server.config["global_scoreboard"])