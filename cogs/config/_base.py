import discord
from discord import app_commands
from discord.ext import commands


class Config(commands.Cog):
    config = app_commands.Group(
        name="config",
        description="Settings to configure the bot's functions.",
        default_permissions=discord.Permissions(manage_guild=True),
    )
