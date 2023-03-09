from cogs.automatic._base import AutoBase
from discord.ext import tasks


class FileWatcher(AutoBase):
    @tasks.loop(minutes=60)
    async def file_mon(self):
        for dir in self.bot.dirList:
            dir.updateFiles()
