from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        """Check if the user is an admin"""
        if ctx.author.id not in self.bot.admins:
            return False
        else:
            return True
        
