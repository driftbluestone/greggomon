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

            buttonstyle = discord.ButtonStyle.primary
            if value["type"] == "bool" and server.config[config]: buttonstyle = discord.ButtonStyle.success
            elif value["type"] == "bool" and not server.config[config]: buttonstyle = discord.ButtonStyle.danger

            button = discord.ui.Button(label = value["display_name"], style=buttonstyle, custom_id=config)
            button.callback = self.open_modal_button_callback
            self.add_item(button)
    # function that is run when button is pressed
    async def open_modal_button_callback(self, interaction: discord.Interaction):
        server = self.server
        if await permissions.check_permission(interaction, server.admins): return await permissions.fail_permission_check(interaction)
        config = interaction.data["custom_id"]
        old_interaction = self.old_interaction
        current_config = configs[config]
        
        if current_config["type"] == "bool":
            server.config[config] = not server.config[config]
            await interaction.response.defer(ephemeral=True, thinking=False)
            embed = generate_config_table(server)
            view = Config_Button(server, old_interaction)
            await update_config_embed(server, old_interaction, embed, view)
        elif current_config["type"] == "special":
            embed = generate_image_set_table(server)
            view = Image_Sets(server, old_interaction)
            await interaction.response.defer(ephemeral=True, thinking=False)
            await old_interaction.edit_original_response(embed=embed, view=view)
        else:
            await interaction.response.send_modal(answer_input(server, old_interaction, config, current_config["display_name"], get_minmax_ranges(server, config)))
            
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
        if await permissions.check_permission(interaction, server.admins): return await permissions.fail_permission_check(interaction)
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
            if len(server.config["image_sets"]) == 1: return await interaction.response.send_message("You must have at least one active image set.",ephemeral=True)
            server.config["image_sets"].remove(button)
        embed = generate_image_set_table(server)
        view = Image_Sets(server, old_interaction)
        await update_config_embed(server, old_interaction, embed, view)
        await interaction.response.defer(ephemeral=True, thinking=False)

async def update_config_embed(server, old_interaction, embed, view):
    await save_server_state(server.id)
    
    await old_interaction.edit_original_response(embed=embed, view=view) 

def get_minmax_ranges(server, config):
    min_max_bound = []
    bounds = ["lower_bound", "upper_bound"]
    for bound in bounds:
        if type(config[bound]) == int:
            bound_value = config[bound]
        elif type(config[bound]) == dict:
            values = []
            for limit in config[bound].keys():
                if limit == "must_be_below":
                    for value in config[bound]:
                        if type(value) == int:
                            values.append(value)
                        else:
                            values.append(server.config[value]-1)
                elif limit == "must_be_above":
                    for value in config[bound]:
                        if type(value) == int:
                            values.append(value)
                        else:
                            values.append(server.config[value]+1)
            if bound == "lower_bound":
                bound_value = min(values)
            elif bound == "upper_bound":
                bound_value = max(values)
        min_max_bound.append(bound_value)
    return min_max_bound
    

def generate_config_table(server):
    description = "### Config\n"
    image = []
    for i in server.config["image_sets"]:
        image.append(image_sets[i])
    for k in configs.keys():
        if not k == "image_sets":
            description+=f"{configs[k]["display_name"]}: {server.config[k]}\n"
        else:
            description+=f"{configs[k]["display_name"]}: {image}\n"
    return discord.Embed(description=description)

def generate_image_set_table(server):
    description = "### Enabled Image Sets\n"
    for i in server.config["image_sets"]:
        description+=f"- {image_sets[i]}\n"

    return discord.Embed(description=description)
            