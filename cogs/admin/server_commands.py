from ._base import Admin
from discord.ext import commands
import utils

class ServerCommands(Admin):
    @commands.command()
    async def info(self, ctx: commands.Context, id: str):
        try:
            _id = int(id)
        except ValueError:
            return await ctx.author.send(embed=utils.embeds.MEE6Embed.error("Whoops", "You have entered an invalid ID"))
        
        try:
            guild = await self.bot.fetch_guild(_id)
        except commands.errors.CommandInvokeError:
            return await ctx.author.send(embed=utils.embeds.MEE6Embed.error("Whoops", "That server does not exist"))

        # TODO: Fetch info about the server and format into an embed
    