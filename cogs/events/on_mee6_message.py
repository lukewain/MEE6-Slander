from ._base import Events
from discord.ext.commands import Cog
from discord.utils import utcnow
from utils import constants
from discord import Message, Embed, Colour, abc


class MEE6Message(Events):
    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.guild or message.author.id != constants.MEE6_ID or "you just advanced" not in message.content:
            return

        slander = self.bot.slander_manager.get_slander(message.guild)
        await message.reply(content=slander)
        await self.increment_status(message, slander)

        log_channel = self.bot.get_channel(constants.SLANDER_LOG_CHANNEL)

        if not log_channel:
            log_channel = await self.bot.fetch_channel(constants.SLANDER_LOG_CHANNEL)

        if not isinstance(log_channel, abc.Messageable):
            return

        embed = Embed(colour=Colour.blurple(), timestamp=utcnow())
        embed.set_author(name="New Slander!")
        embed.add_field(name="Server ID", value=message.guild.id, inline=False)
        embed.add_field(name="Server Name", value=message.guild.name, inline=False)
        embed.add_field(name="Slander Sent", value=f"`{slander}`", inline=False)

        await log_channel.send(embed=embed)
