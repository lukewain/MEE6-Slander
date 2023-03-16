from src.bot import MEE6Slander
import asyncio
import asyncpg
import os
import dotenv

from dotenv import load_dotenv

load_dotenv()



async def run():
    async with MEE6Slander(dsn=os.environ['PG_DSN']) as bot:
        await bot.start(bot.token)


asyncio.run(run())
