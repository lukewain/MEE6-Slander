from cogs.automatic.fileListener import FileWatcher


async def setup(bot):
    await bot.add_cog(FileWatcher(bot))
