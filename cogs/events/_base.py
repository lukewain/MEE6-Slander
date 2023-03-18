from discord.ext.commands import Cog
import discord
from json import load, dump
import utils
from src.bot import MEE6Slander as Bot


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_load(self):
        utils.log("Events cog has loaded!")

        self.status_int: int = 0

    async def increment_status(self, message: discord.Message, slander: str):
        insert = await self.bot.pool.execute("INSERT INTO slander_log (message, gid, cid, sent) VALUES ($1, $2, $3, $4)", slander, message.guild.id, message.channel.id, discord.utils.utcnow().timestamp()) # type: ignore

        if not insert:
            return await self.bot._log_webhook.send(content="Something went wrong tracking the slander")

        total = await self.bot.pool.fetchval("SELECT count(*) FROM slander_log")
        
        if total % 5 == 0:
            await self.bot.change_presence(
                    status=discord.Status.online,
                    activity=discord.Game(name=f"Slandered MEE6 {total} times!"),
                )
