from ._base import Events
from discord.ext.commands import Cog
from discord.utils import utcnow
from utils import constants, log
from discord import Message, Embed, Colour
from random import choice


class MEE6Message(Events):
    @Cog.listener()
    async def on_message(self, message: Message):
        if (
            message.author.id == constants.MEE6_ID
            and "you just advanced" in message.content
        ):
            with open("src/slander.txt") as slander:
                slanderlines = slander.readlines()

            slan = choice(slanderlines).strip()
            await message.reply(content=slan)
            await self.increment_status()

            chnl = await self.bot.fetch_channel(constants.SLANDER_LOG_CHANNEL)
            embed = Embed(colour=Colour.blurple())
            embed.set_author(name="New Slander!")
            embed.add_field(name="Server ID", value=message.guild.id, inline=False)
            embed.add_field(name="Server Name", value=message.guild.name, inline=False)
            embed.add_field(name="Slander Sent", value=f"`{slan}`", inline=False)
            embed.set_footer(text=utcnow())

            await chnl.send(embed=embed)