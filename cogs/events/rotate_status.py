from ._base import Events
from discord import Game, Status
from discord.ext import tasks

from json import load

class RotateStatus(Events):
    async def cog_load(self):
        self.status_int = 1
        self.rotate_status.start()

    async def before_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def rotate_status(self):
        if self.status_int == 1:
            with open("./total_slander.json") as tsf:
                total = load(tsf)
                total_slander = total['total']
            await self.bot.change_presence(
                status=Status.online,
                activity=Game(f"Slandered MEE6 {total_slander} times")
            )
            self.status_int += 1

        elif self.status_int == 2:
            await self.bot.change_presence(
                status=Status.online,
                activity=Game(f"Watching for MEE6 in {len(self.bot.guilds)} servers")
            )
            self.status_int = 1
