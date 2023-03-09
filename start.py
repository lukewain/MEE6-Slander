from src.bot import MEE6Slander
import asyncio
import asyncpg
import os
import dotenv

from dotenv import load_dotenv; load_dotenv()

DSN = f"postgres://{os.environ['DBUSER']}:{os.environ['DBPASS']}@192.168.1.124/{os.environ['DBNAME']}"

async def run():
    async with (
        asyncpg.create_pool(DSN) as pool,
        MEE6Slander(pool=pool) as bot
    ):
        await bot.start(bot.token)


asyncio.run(run())
