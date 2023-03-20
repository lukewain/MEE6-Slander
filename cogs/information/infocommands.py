import datetime
from email import message
import typing
from ._base import Information

import discord
from discord.ext import commands

from typing import Any

import asyncpg
import time

from src.bot import MEE6Slander

class InfoCommands(Information):
    @commands.hybrid_command(name="uptime", aliases=["up", "ut"])
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

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context[MEE6Slander]):
        """Show the latency of all the services on the bot"""

        pings: list[Any] = []
        number = 0

        # Typing Latency
        typing_start: float = time.monotonic()
        await ctx.typing()
        typing_end: float = time.monotonic()
        typing_ms: float = (typing_end - typing_start) * 1000
        pings.append(typing_ms)

        # Message Latency
        message_start: float = time.monotonic()
        await ctx.send("Pong 🏓!")
        message_end: float = time.monotonic()
        message_ms: float = (message_end - message_start) * 1000
        pings.append(message_ms)

        # Websocket Latency
        latency_ms: float = ctx.bot.latency * 1000
        pings.append(latency_ms)

        # Database Latency
        pg_start: float = time.monotonic()
        await ctx.bot.pool.fetch("SELECT 1")
        pg_end: float = time.monotonic()
        pg_ms: float = (pg_end - pg_start) * 1000
        pings.append(pg_ms)

        for ms in pings:
            number += ms

        avg_ms = number / len(pings)
        
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.add_field(name="Websocket", value=f"`{latency_ms}ms`", inline=False)
        embed.add_field(name="Typing", value=f"`{typing_ms}ms`", inline=False)
        embed.add_field(name="Message", value=f"`{message_ms}ms`", inline=False)
        embed.add_field(name="Database", value=f"`{pg_ms}ms`", inline=False)
        embed.add_field(name="Average", value=f"`{avg_ms}ms`", inline=False)

        await ctx.send(embed=embed)
