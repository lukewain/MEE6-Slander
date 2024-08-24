import asyncio
import aiohttp

from prisma import Prisma

from src.bot import MEE6Slander
from utils import SlanderManager, Config

config = Config.load_config()

channel_id = config.queue_cid
anyone_can_click = config.anyone_can_click
dev_mode = config.developer_mode


async def run():
    p = await Prisma.connect()
    async with aiohttp.ClientSession() as session:
        manager = SlanderManager(
            prisma=p, queue_channel_id=channel_id, anyone_can_click=anyone_can_click
        )
        async with MEE6Slander(
            prisma=p, slander_manager=manager, aiosession=session, config=config
        ) as bot:
            await bot.create_tables()
            await manager.start()
            await manager.register_views(bot)
            await bot.start(bot.token)


asyncio.run(run())
