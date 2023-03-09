from discord import errors
from discord.ext import commands

from utils import error

class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Event is triggered on command error"""

        if hasattr(ctx.command, "on_error"):
            return
        
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
            
        error(f"{ctx.author.name} tried to use command {ctx.message.content}")


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))