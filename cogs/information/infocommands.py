import datetime
from pydoc import describe
from _base import Information

import discord
from discord.ext import commands

import asyncpg
import time

from src.bot import MEE6Slander

class InfoCommands(Information):
    @commands.hybrid_command(name="upime", aliases=["up", "ut"])
    async def uptime(self, ctx: commands.Context[MEE6Slander]):
        """Show the user the uptime of the bot"""
        online_since: int = ctx.bot.start_time
        online_for: int = round(time.time()) - ctx.bot.start_time

        embed = discord.Embed(
            title="Uptime",
            colour=discord.Colour.blue()
        )

        embed.add_field(name="Online Since", value=f"<t:{online_since}:F", inline=False)
        embed.add_field(name="Online For", value=datetime.timedelta(seconds=online_for))

        await ctx.send(embed=embed)
