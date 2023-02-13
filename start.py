from src.bot import MEE6Slander
import asyncio


async def run():
    async with MEE6Slander() as bot:
        await bot.start(bot.token)


asyncio.run(run())
