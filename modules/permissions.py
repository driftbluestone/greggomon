import discord
from modules.classes import *
from modules.data import *

async def check_permission(interaction: discord.Interaction, admins):
    user_id = str(interaction.user.id)
    if user_id in admins:
        return False
    else:
        return True

async def fail_permission_check(interaction: discord.Interaction):
    await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

async def promote(interaction: discord.Interaction, user: discord.User, server: Server):
    user_id = str(user.id)
    if user_id not in server.admins:
        server.admins.append(user_id)
        await interaction.response.send_message(f"{user.name} has been promoted to admin!")
    else:
        server.admins.remove(user_id)
        await interaction.response.send_message(f"{user.name} has been demoted.")
    await save_server_state(server.id)
