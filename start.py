import asyncio
import aiohttp

import asyncpg

from src.bot import MEE6Slander
from utils import SlanderManager, Config

config = Config.load_config()

channel_id = config.queue_cid
anyone_can_click = config.anyone_can_click
dev_mode = config.developer_mode


async def run():
    async with asyncpg.create_pool(
        config.dev_dsn if dev_mode else config.pg_dsn
    ) as pool, aiohttp.ClientSession() as session:
        manager = SlanderManager(
            pool=pool, queue_channel_id=channel_id, anyone_can_click=anyone_can_click
        )
        async with MEE6Slander(
            pool=pool, slander_manager=manager, aiosession=session, config=config
        ) as bot:
            await bot.create_tables()
            await manager.start()
            await manager.register_views(bot)
            await bot.start(bot.token)


asyncio.run(run())
