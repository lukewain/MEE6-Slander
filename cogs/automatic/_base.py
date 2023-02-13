from discord.ext.commands import Cog
from src.bot import MEE6Slander


class AutoBase(Cog):
    def __init__(self, bot: MEE6Slander):
        self.bot = bot

    async def cog_load(self):
        ...

    async def cog_check(self):
        ...
