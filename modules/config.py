import discord, json, pathlib
from classes import *
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/../data/config_config.json") as file:
    configs = json.load(file)
class Config_Creator():
    def __init__(self, config):
        self.config = config
mymodal = 0
class Config_Button(discord.ui.View):
    def __init__(self, server, config):
        super().__init__(timeout=1000000000)
        self.server: Server
        self.server = server
        self.config = config
        button = discord.ui.button(
            label = config[0],
            style=discord.ButtonStyle.primary,
            custom_id=f"config_{config[0]}"
        )
        button.callback = self.open_modal_button_callback
        self.add_item(button)

    async def open_modal_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("config toggled")