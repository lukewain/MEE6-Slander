from src.bot import MEE6Slander

from .slander_settings import SlanderSettings


class Config(SlanderSettings):
    """Configure the functions of the bot itself."""


async def setup(bot: MEE6Slander):
    await bot.add_cog(Config(bot))
