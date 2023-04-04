import os
import asyncio
import aiohttp

import asyncpg
from dotenv import load_dotenv

from src.bot import MEE6Slander
from utils import SlanderManager

load_dotenv()

channel_id = int(os.environ["QUEUE_CHID"])
anyone_can_click = os.environ["ANYONE_CAN_CLICK"] == "True"
dev_mode = os.environ["DEV"] == "True"


async def run():
    async with asyncpg.create_pool(
        os.environ["PG_DSN"]
    ) as pool, aiohttp.ClientSession() as session:
        manager = SlanderManager(
            pool=pool, queue_channel_id=channel_id, anyone_can_click=anyone_can_click
        )
        async with MEE6Slander(
            pool=pool, slander_manager=manager, aiosession=session, dev_mode=dev_mode
        ) as bot:
            await bot.create_tables()
            await manager.start()
            await manager.register_views(bot)
            await bot.start(bot.token)


asyncio.run(run())
