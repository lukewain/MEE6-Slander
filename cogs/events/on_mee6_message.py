from ._base import Events
from discord.ext.commands import Cog
from discord.utils import utcnow
from utils import constants, log
from discord import Message, Embed, Colour, abc
from random import choice


class MEE6Message(Events):
    @Cog.listener()
    async def on_message(self, message: Message):
        if (
            message.author.id == constants.MEE6_ID
            and "you just advanced" in message.content
        ):
            with open("src/slander.txt") as slander:
                slander_lines = slander.readlines()

            slander = choice(slander_lines).strip()
            await message.reply(content=slander)
            await self.increment_status()

            slander = await self.bot.fetch_channel(constants.SLANDER_LOG_CHANNEL)

            if not isinstance(slander, abc.Messageable) or not message.guild:
                return

            embed = Embed(colour=Colour.blurple())
            embed.set_author(name="New Slander!")
            embed.add_field(name="Server ID", value=message.guild.id, inline=False)
            embed.add_field(name="Server Name", value=message.guild.name, inline=False)
            embed.add_field(name="Slander Sent", value=f"`{slander}`", inline=False)
            embed.set_footer(text=utcnow())

            await slander.send(embed=embed)