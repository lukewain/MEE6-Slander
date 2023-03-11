from ._base import Stats
from discord.ext.commands import Context
from discord.ext import commands

from utils.embeds import MEE6Embed


class StatsCommands(Stats):
    @commands.command()
    async def stats(self, ctx: Context):
        await ctx.send(
            embed=MEE6Embed.stats_embed(
                self.msg_count,
                self.del_count,
                self.edit_count,
                self.servers_joined,
                self.servers_left,
                self.slanders_sent,
                self.start_time,
                self.bot.user.avatar.url,
            )
        )
