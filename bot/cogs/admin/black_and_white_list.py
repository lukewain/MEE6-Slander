from discord.ext import commands

from src.bot import MEE6Slander

from ._base import Admin


class BlackandWhiteList(Admin):
    @commands.command(name="blacklist")
    async def blacklist(self, ctx: commands.Context[MEE6Slander], user_id: str):
        ...

    
    @commands.command(name="whitelist")
    async def whitelist(self, ctx: commands.Context[MEE6Slander])
        