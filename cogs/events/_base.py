from discord.ext.commands import Cog, Bot
from discord import Game, Status
from json import load, dump
import utils


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_load(self):
        utils.log("Events cog has loaded!")

        self.status_int: int = 0

    async def increment_status(self):
        with open("./total_slander.json", "r") as totalslander:
            total = load(totalslander)
            total["total"] += 1
            await self.bot.change_presence(
                status=Status.online,
                activity=Game(name=f"Slandered MEE6 {total['total']} times!"),
            )
        
        with open("./total_slander.json", "w") as totalslander:
            dump(total, totalslander)
        
