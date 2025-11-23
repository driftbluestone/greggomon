import discord, pathlib, os, shutil, json, time, random, autocorrect
bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/TOKEN.txt", "r") as file:
    TOKEN = file.read()
with open(f"{DIR}/gtceum.json", "r") as file:
    gtceum = json.load(file)

# configs to eventually outsource to json
max_guess_length = 75

@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as exception:
        print(f"Error syncing commands: {exception}")
    print(f'Gregging it up as {bot.user}!')

# data storage objects
class server:
    def __init__(self, id, config):
        self.id = id
        self.config = config

# discord interaction buttons
class answer_button(discord.ui.View):
    @discord.ui.button(label="Submit a Guess!", style=discord.ButtonStyle.primary, custom_id="open_modal_button")
    async def open_modal_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(answer_input())

class answer_input(discord.ui.Modal, title="Submit a Guess"):
    my_input = discord.ui.TextInput(
        label="Enter your guess:",
        placeholder="",
        style=discord.TextStyle.short, # discord.TextStyle.paragraph for multi line
        required=True,
        max_length=max_guess_length
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.my_input.value
        #await interaction.response.edit_message(content="Button clicked!", view=None)
        await answer_logic(interaction, user_input)

@tree.command(name="image",description="Resends the previous image")
async def image(interaction:discord.Interaction):
    image, link = random.choice(list(gtceum.items()))
    embed=discord.Embed(title=image)
    embed.set_image(url=link)
    await interaction.response.send_message(embed=embed,view=answer_button())

@tree.command(name="newimage",description="Send a random image")
async def image(interaction:discord.Interaction):
    image, link = random.choice(list(gtceum.items()))
    embed=discord.Embed(title=image)
    embed.set_image(url=link)
    await interaction.response.send_message(embed=embed,view=answer_button())

@tree.command(name="answer",description="Submit a guess on the current image")
async def image(interaction:discord.Interaction, guess: str):
    await answer_logic(interaction, guess)

async def answer_logic(interaction: discord.Interaction, guess: str):
    guess_list = autocorrect.correct_input(f" {guess} ", 1).split()
    await interaction.response.send_message(guess_list)

bot.run(TOKEN)
