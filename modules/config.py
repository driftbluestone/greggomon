import discord, json, pathlib
from modules import permissions
from modules.classes import *
from modules.data import save_server_state
DIR = pathlib.Path(__file__).parent.absolute()
with open(f"{DIR}/../data/config_config.json") as file:
    configs = json.load(file)
with open(f"{DIR}/../data/image_sets.json") as file:
    image_sets = json.load(file)

class answer_input(discord.ui.Modal, title="Enter new value"):
    def __init__(self, server, old_interaction, config, name, range):
        super().__init__()
        self.server = server
        self.old_interaction = old_interaction
        self.config = config
        self.name = name
        self.range = range
        self.user_input = discord.ui.TextInput(
            label=f"Enter a number between {range[0]} and {range[1]}.",
            placeholder="",
            style=discord.TextStyle.short,
            required=True,
            max_length=10
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        value = self.user_input.value
        old_interaction = self.old_interaction
        server = self.server
        try: value = int(value)
        except: return await interaction.response.send_message("Error. Must input an integer.",ephemeral=True)
        if value < self.range[0] or value > self.range[1]: return await interaction.response.send_message(f"{self.name} must be between {self.range[0]} and {self.range[1]}.",ephemeral=True)
        self.server.config[self.config] = value
        embed = generate_config_table(server)
        view = Config_Button(server, old_interaction)
        await update_config_embed(server, old_interaction, embed, view)
        await interaction.response.defer(ephemeral=True, thinking=False)
        
class Config_Button(discord.ui.View):
    def __init__(self, server, old_interaction):
        super().__init__(timeout=1000000000)
        self.server: Server = server
        self.old_interaction: discord.Interaction = old_interaction
        for config, value in configs.items():
            button = discord.ui.Button(label = value[0], style=discord.ButtonStyle.primary, custom_id=config)
            button.callback = self.open_modal_button_callback
            self.add_item(button)
    async def open_modal_button_callback(self, interaction: discord.Interaction):
        server = self.server
        if await permissions.check_permission(interaction, server.admins): return await permissions.fail_permission_check(interaction)
        config = interaction.data["custom_id"]
        old_interaction = self.old_interaction
        name = configs[config][0]
        ranges = {}
        for k, v in configs.items():
            ranges[k] = v[1]
        
        if ranges[config] == "bool":
            server.config[config] = not server.config[config]
            await interaction.response.defer(ephemeral=True, thinking=False)
            embed = generate_config_table(server)
            view = Config_Button(server, old_interaction)
            await update_config_embed(server, old_interaction, embed, view)
        elif ranges[config] == "list":
            embed = generate_image_set_table(server)
            view = Image_Sets(server, old_interaction)
            await interaction.response.defer(ephemeral=True, thinking=False)
            await old_interaction.edit_original_response(embed=embed, view=view)
        else:
            min_max_values = ranges[config]
            if ranges[config] == "varies" or ranges[config][1] == "varies": min_max_values = get_minmax_ranges(server, config)
            await interaction.response.send_modal(answer_input(server, old_interaction, config, name, min_max_values))
            
class Image_Sets(discord.ui.View):
    def __init__(self, server, old_interaction):
        super().__init__(timeout=1000000000)
        self.server: Server = server
        self.old_interaction: discord.Interaction = old_interaction
        for set, title in image_sets.items():
            button = discord.ui.Button(label = title, style=discord.ButtonStyle.primary, custom_id=set)
            button.callback = self.open_modal_button_callback
            self.add_item(button)
    async def open_modal_button_callback(self, interaction: discord.Interaction):
        server = self.server
        old_interaction = self.old_interaction
        button = interaction.data["custom_id"]
        if button == "back":
            embed = generate_config_table(server)
            view = Config_Button(server, old_interaction)
            await interaction.response.defer(ephemeral=True, thinking=False)
            return await update_config_embed(server, old_interaction, embed, view)
        if button not in server.config["image_sets"]:
            server.config["image_sets"].append(button)
        else:
            server.config["image_sets"].remove(button)
        embed = generate_image_set_table(server)
        view = Image_Sets(server, old_interaction)
        await update_config_embed(server, old_interaction, embed, view)
        await interaction.response.defer(ephemeral=True, thinking=False)

async def update_config_embed(server, old_interaction, embed, view):
    await save_server_state(server.id)
    
    await old_interaction.edit_original_response(embed=embed, view=view) 

# outsource this to a json later, somehow
def get_minmax_ranges(server, config):
    if config == "user_guess_limit":
        if server.config["universal_guess_limit"]:
            min_value = 0
        else:
            min_value = 1
        if server.config["guesses_to_hint"] > 5:
            max_value = 5
        else:
            max_value = server.config["guesses_to_hint"]-1
    elif config == "time_to_primary_skip":
        min_value = 5
        max_value = server.config["time_to_secondary_skip"]-1
    elif config == "time_to_secondary_skip":
        min_value = server.config["time_to_primary_skip"]+1
        max_value = 1440
    elif config == "guesses_to_hint":
        min_value = server.config["user_guess_limit"]+1
        max_value = 10000
    return [min_value, max_value]

def generate_config_table(server):
    description = "### Config\n"
    image = []
    for i in server.config["image_sets"]:
        image.append(image_sets[i])
    for k in configs.keys():
        if not k == "image_sets":
            description+=f"{configs[k][0]}: {server.config[k]}\n"
        else:
            description+=f"{configs[k][0]}: {image}\n"
    return discord.Embed(description=description)

def generate_image_set_table(server):
    description = "### Enabled Image Sets\n"
    for i in server.config["image_sets"]:
        description+=f"- {image_sets[i]}\n"

    return discord.Embed(description=description)
            