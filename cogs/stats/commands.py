import typing

import discord
from ._base import Stats
from discord.ext.commands import Context
from discord.ext import commands

from utils.embeds import MEE6Embed


class StatsCommands(Stats):
    @commands.command()
    async def stats(self, ctx: Context):
        all_time = await self.bot.pool.fetchval("SELECT count(*) FROM messages")
        await ctx.send(
            embed=MEE6Embed.stats_embed(
                self.msg_count,
                int(all_time),
                self.del_count,
                self.edit_count,
                self.servers_joined,
                self.servers_left,
                self.slanders_sent,
                self.start_time,
                self.bot.user.display_avatar.url if self.bot.user else "",
            )
        )

    @commands.hybrid_command(
        name="suggestions", description="See the number of suggestions sent by a user."
    )
    async def suggestions(self, ctx: Context, *, user: typing.Optional[discord.Member]):
        ...
        if not user:
            search_id: int = ctx.author.id
        else:
            search_id: int = user.id

        total_slanders: int = await self.bot.pool.fetchval(
            "SELECT count(*) from slanders WHERE creator=$1", search_id
        )
        approved: int = await self.bot.pool.fetchval(
            "SELECT count(*) FROM slanders WHERE creator=$1 AND approved=True",
            search_id,
        )
        awaiting: int = await self.bot.pool.fetchval(
            "SELECT count(*) FROM slanders WHERE creator=$1 AND approved=$2",
            search_id,
            None,
        )
        denied: int = await self.bot.pool.fetchval(
            "SELECT count(*) FROM slanders WHERE creator=$1 AND approved=False",
            search_id,
        )

        # TODO: create the embed with :green_square: for approved, :orange_square: for not approved yet, :red_square: for denied ones, :white_large_square: for total

        embed = discord.Embed(
            title="Slander Stats",
            description=f"Slander stats for {ctx.author if not user else user}",
        )

        embed.add_field(
            name=":green_square: Slanders Approved", value=f"{approved}", inline=False
        )
        embed.add_field(
            name=":orange_square: Slanders Awaiting Approval",
            value=f"{awaiting}",
            inline=False,
        )
        embed.add_field(
            name=":red_square: Slanders Denied", value=f"{denied}", inline=False
        )
        embed.add_field(
            name=":white_large_square: Total Slanders",
            value=f"{total_slanders}",
            inline=False,
        )

        return await ctx.send(embed=embed)
