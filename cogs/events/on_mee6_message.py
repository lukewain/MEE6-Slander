import discord
from cogs.stats import commands

import utils
from ._base import Events
from discord.ext.commands import Cog
from discord.utils import utcnow
from utils import constants
from discord import Message, Embed, Colour, abc

from random import randint


class MEE6Message(Events):
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id == constants.MEE6_ID:
            await self.bot._log_webhook.send(
                embed=discord.Embed(title="MEE6 Message", description=message.content)
            )

        if not message.guild or message.author.id != constants.MEE6_ID:
            return

        slander = self.bot.slander_manager.get_slander(guild=message.guild)
        await message.reply(content=slander)
        self.bot.dispatch("slander")
        if self.bot.show_support_link and randint(0, 100) < 10:
            utils.log("Notified about support server", "WARN")
            await message.channel.send(
                embed=discord.Embed(
                    title="Support Server",
                    description=f"MEE6 Slander support server is now live. Join [here]({self.bot.support_link})",
                )
            )
        await self.increment_status(message, slander)

        log_channel = self.bot.get_channel(constants.SLANDER_LOG_CHANNEL)

        if not log_channel:
            log_channel = await self.bot.fetch_channel(constants.SLANDER_LOG_CHANNEL)

        if not isinstance(log_channel, abc.Messageable):
            return

        # Get total slanders
        total_slanders = await self.bot.pool.fetchval(
            "SELECT count(*) FROM slander_log"
        )

        embed = Embed(colour=Colour.blurple(), timestamp=utcnow())
        embed.set_author(name=f"New Slander! #{total_slanders}")
        embed.add_field(name="Server ID", value=message.guild.id, inline=False)
        embed.add_field(name="Server Name", value=message.guild.name, inline=False)
        embed.add_field(name="Slander Sent", value=f"`{slander}`", inline=False)

        await log_channel.send(embed=embed)
