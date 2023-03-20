from .infocommands import InfoCommands

class InformationCog(InfoCommands):
    """A cog for all the information commands"""


async def setup(bot):
    await bot.add_cog(InformationCog())