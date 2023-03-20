from __future__ import annotations
import os
import aiohttp

import discord
from discord.ext.commands import Bot
from discord import DiscordException, Intents, AllowedMentions, Status, Game
from discord.utils import setup_logging

from os import environ
from dotenv import load_dotenv
import time
import asyncpg

from json import load


import utils
from .tree import SlanderTree

load_dotenv()
setup_logging()


class MEE6Slander(Bot):
    def __init__(self, *, pool: asyncpg.Pool[asyncpg.Record], slander_manager: utils.SlanderManager, aiosession: aiohttp.ClientSession, dev_mode: bool):
        # Define the bot's intents
        intents: Intents = Intents().default()
        intents.message_content = True
        intents.members = True

        self.prefix: str = environ['PREFIX'] if not dev_mode else environ['DEV_PREFIX']

        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

        super().__init__(command_prefix=self.prefix, intents=intents, allowed_mentions=allowed_mentions, tree_cls=SlanderTree)

        self.dev_mode: bool = dev_mode # type: ignore
        self.token: str = environ["TOKEN"] if not dev_mode else environ['DEV_TOKEN']

        self.github: str = "https://github.com/lukewain/MEE6-Slander"

        self.support_link: str = "https://discord.gg/EQpxMZSFy3"
        self.show_support_link: bool = os.environ["SHOW_SUPPORT_LINK"] == "True"

        self.pool: asyncpg.Pool[asyncpg.Record] = pool
        self.slander_manager: utils.SlanderManager = slander_manager
        self._session: aiohttp.ClientSession = aiosession

        self.start_time: int = round(time.time())

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.config")
        await self.load_extension("cogs.suggest")

        self._log_webhook: discord.Webhook = discord.Webhook.from_url(url=os.environ['WEBHOOK_URL'], session=self._session, bot_token=self.token)

    async def create_tables(self):
        self.total = await self.pool.fetchval("SELECT count(*) FROM slander_log")

        with open("./src/schema.sql") as file:
            await self.pool.execute(file.read())
        utils.log("Schema successfully uploaded")

    async def on_ready(self) -> None:
        utils.log(f"Logged in as {self.user}")
        await self.change_presence(
            status=Status.online,
            activity=Game(name=f"Slandered MEE6 {self.total} times!"),
        )
