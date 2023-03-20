import asyncpg
import discord
from discord import app_commands
from discord.ext import commands

from src.bot import MEE6Slander

class Information(commands.Cog):
    async def interaction_check(self, interaction: discord.Interaction[MEE6Slander]):
        # Check if the user is in the blacklist db
        res: asyncpg.Record | None = await interaction.client.pool.fetchrow("SELECT * FROM blacklist WHERE id=$1", interaction.user.id)

        if not res:
            return True
        
        return False
        
    async def cog_check(self, ctx: commands.Context[MEE6Slander]):
        # Check if the user is in the blacklist db
        res: asyncpg.Record | None = await ctx.bot.pool.fetchrow("SELECT * FROM blacklist WHERE id=$1", ctx.author.id)

        if not res:
            return True
        
        return False