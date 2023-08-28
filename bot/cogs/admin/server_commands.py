import discord
from src.bot import MEE6Slander
from ._base import Admin
from discord.ext import commands
import utils

import logging

log = logging.getLogger(__name__)


class ServerCommands(Admin):
    @commands.command()
    async def info(self, ctx: commands.Context[MEE6Slander], id: str):
        try:
            _id = int(id)
        except ValueError:
            return await ctx.author.send(
                embed=utils.embeds.MEE6Embed.error(
                    "Whoops", "You have entered an invalid ID"
                )
            )

        try:
            guild = self.bot.get_guild(_id)
            if guild is None:
                guild = await self.bot.fetch_guild(_id)
        except commands.errors.CommandInvokeError:
            return await ctx.author.send(
                embed=utils.embeds.MEE6Embed.error(
                    "Whoops", "That server does not exist"
                )
            )

        # TODO: Fetch info about the server and format into an embed

    @commands.command(name="announce")
    @commands.is_owner()
    async def announce(self, ctx: commands.Context[MEE6Slander], *, message: str):
        if len(message) > 4096:
            return await ctx.send("That announcement is too long.")

        embed = discord.Embed(title="Announcement!", description=message)
        embed.set_footer(text=f"Sent by {ctx.author}")

        sent = 0

        for guild in self.bot.guilds:
            # Fetch guild alert channel info from db
            cid = await ctx.bot.pool.fetchval(
                "SELECT alert_cid FROM guilds WHERE id=$1", guild.id
            )

            if cid is None:
                alert_channel = guild.public_updates_channel

                if not alert_channel:
                    log.warn(f"{guild.name} has no public updates channel!")
                    
                    continue
            else:
                alert_channel = ctx.bot.get_channel(cid)

                if alert_channel is None:
                    alert_channel = await ctx.bot.fetch_channel(cid)

            try:
                await alert_channel.send(embed=embed)
                sent += 1
            except:
                log.error(f"Unable to announce in {guild.name}")

        await ctx.send(f"Announced to {sent}/{len(self.bot.guilds)} guilds!")
