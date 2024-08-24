from prisma import Prisma, models
import discord
from discord import app_commands
from discord.ext import commands

from src.bot import MEE6Slander

class Information(commands.Cog):
    async def interaction_check(self, interaction: discord.Interaction[MEE6Slander]):
        # Check if the user is in the blacklist db
        res: models.BlackList | None = await interaction.client.prisma.blacklist.find_unique(where={"id": interaction.user.id})

        if not res:
            return True
        
        return await interaction.response.send_message(embed=discord.Embed(title="Whoops", description="You do not have permission to do that!"))
        
    async def cog_check(self, ctx: commands.Context[MEE6Slander]):
        # Check if the user is in the blacklist db
        res: models.BlackList | None = await ctx.bot.prisma.blacklist.find_unique(where={"id": ctx.author.id})

        if not res:
            return True
        
        return await ctx.send(embed=discord.Embed(title="Whoops", description="You do not have permission to do that!"))