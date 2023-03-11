from discord.ext.commands import Cog
from discord.utils import utcnow
from src.bot import MEE6Slander


class Stats(Cog):
    def __init__(self, bot: MEE6Slander):
        self.bot = bot

        # Stats for the cog, resets on restart
        self.msg_count = 0
        self.del_count = 0
        self.edit_count = 0
        self.servers_joined = 0
        self.servers_left = 0
        self.slanders_sent = 0

    async def cog_load(self):
        self.start_time = round(utcnow().timestamp())
