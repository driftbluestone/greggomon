import discord
from modules.answer_logic import answer_logic
from modules.classes import *
class answer_button(discord.ui.View):
    def __init__(self, server, bot):
        super().__init__(timeout=1000000000)
        self.bot = bot
        self.server: Server = server
    @discord.ui.button(label="Submit a Guess!", style=discord.ButtonStyle.primary, custom_id="open_modal_button")
    async def open_modal_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(answer_input(self.server, self.bot))

class answer_input(discord.ui.Modal, title="Submit a Guess"):
    def __init__(self, server, bot):
        super().__init__()
        self.server: Server = server
        self.bot = bot
        self.user_input = discord.ui.TextInput(
            label="Enter your guess:",
            placeholder="",
            style=discord.TextStyle.short, # discord.TextStyle.paragraph for multi line
            required=True,
            max_length=self.server.config["max_guess_length"]
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.user_input.value
        await answer_logic(interaction, user_input, self.bot)
