from .server_commands import ServerCommands

class AdminCommands(ServerCommands):
    """All the admin commands for the bot"""


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))