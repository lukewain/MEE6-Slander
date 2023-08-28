from ._base import Events
import discord
from discord.ext import commands
from discord.ext.commands import Cog

import utils


class MemberJoinLeave(Events):
    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.join_leave_webhook.send(
            username="MEE6 Slander Join",
            avatar_url=self.bot.user.display_avatar.url,
            embed=discord.Embed(title="Member Joined!", colour=discord.Colour.green())
            .add_field(name="User Name", value=member, inline=False)
            .add_field(name="Server Name", value=member.guild.name, inline=False)
            .add_field(name="Member ID", value=member.id, inline=False),
        )

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot.join_leave_webhook.send(
            username="MEE6 Slander Leave",
            avatar_url=self.bot.user.display_avatar.url,
            embed=discord.Embed(title="Member Left!", colour=discord.Colour.red())
            .add_field(name="User Name", value=member, inline=False)
            .add_field(name="Server Name", value=member.guild.name, inline=False)
            .add_field(name="Member ID", value=member.id, inline=False),
        )
