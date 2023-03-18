import discord
from discord import app_commands
from discord.ext import commands

from src.bot import MEE6Slander


class Config(commands.Cog):
    def __init__(self, bot: MEE6Slander):
        self.bot: MEE6Slander = bot

    config = app_commands.Group(
        name="config",
        description="Settings to configure the bot's functions.",
        default_permissions=discord.Permissions(manage_guild=True),
    )
