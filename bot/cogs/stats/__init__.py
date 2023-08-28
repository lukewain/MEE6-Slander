from .commands import StatsCommands
from .stat_tracker import StatTracker


class StatCog(StatsCommands, StatTracker):
    """The stats cog"""


async def setup(bot):
    await bot.add_cog(StatCog(bot))
