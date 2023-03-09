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

        return await ctx.reply("This command is currently in development!.")
    
    
    ## Commands that are only for the owner
    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def panel(self, ctx: commands.Context):
        return await ctx.reply("https://192.168.1.124:9090/")