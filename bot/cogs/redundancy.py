import discord
from discord.ext import commands

import platform

from src.bot import MEE6Slander

# TODO: Set default server and have it stored in a DB

class Redundancy(commands.Cog):
    def __init__(self, bot: MEE6Slander):
        self.bot = bot
        self.hostname = platform.node()


    @
