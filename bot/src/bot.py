from __future__ import annotations
import os
import aiohttp

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import DiscordException, Intents, AllowedMentions, Status, Game
from discord.utils import setup_logging

import time
from prisma import Prisma
import logging

import utils
from .tree import SlanderTree

setup_logging()

_log = logging.getLogger(__name__)


class MEE6Slander(Bot):
    def __init__(
        self,
        *,
        prisma: Prisma,
        slander_manager: utils.SlanderManager,
        aiosession: aiohttp.ClientSession,
        config: utils.Config,
    ):
        # Define the bots config file
        self.config = config

        # Define the bot's intents
        intents: Intents = Intents().default()
        intents.message_content = True
        intents.members = True

        self.prefix: str = (
            config.prefix if not config.developer_mode else config.developer_prefix
        )
        self.actual_prefix = commands.when_mentioned_or(self.prefix)

        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

        super().__init__(
            command_prefix=self.actual_prefix,
            intents=intents,
            allowed_mentions=allowed_mentions,
            tree_cls=SlanderTree,
        )

        self.dev_mode: bool = config.developer_mode  # type: ignore
        self.token: str = (
            config.token if not config.developer_mode else config.dev_token
        )

        self.join_leave_webhook = discord.Webhook.from_url(
            self.config.join_leave_webhook, session=aiosession
        )

        self.github: str = "https://github.com/lukewain/MEE6-Slander"

        self.support_link: str = "https://discord.gg/EQpxMZSFy3"
        self.show_support_link: bool = config.show_support_link

        self.prisma: Prisma = prisma
        self.slander_manager: utils.SlanderManager = slander_manager
        self._session: aiohttp.ClientSession = aiosession

        self.start_time: int = round(time.time())

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.config")
        await self.load_extension("cogs.suggest")
        await self.load_extension("cogs.stats")

        self._log_webhook: discord.Webhook = discord.Webhook.from_url(
            url=self.config.webhook_url, session=self._session, bot_token=self.token
        )
        
        # Gather all the counter variables
        
        self.message_count = await self.gather_message_count()

    async def create_tables(self):
        with open("./src/schema.sql") as file:
            await self.pool.execute(file.read())
        _log.info("Loaded schema!")
        
        self.total = await self.pool.fetchval("SELECT count(*) FROM slander_log")
        for i in range(self.total):
            if self.total % 5 == 0:
                break
            else:
                self.total -= 1
        
    async def gather_message_count(self) -> int:
        msg_count = await self.pool.fetchval("SELECT cvalue FROM counters WHERE cname='message_count'")
        return msg_count

    async def on_ready(self) -> None:
        _log.info(f"Logged in as {self.user}")
        await self.change_presence(
            status=Status.online,
            activity=Game(name=f"Slandered MEE6 {self.total} times!"),
        )

    async def on_resume(self) -> None:
        _log.info("Session is resumed!")


# TODO: Start on web page for MEE6 Slander. Allow for managing servers and features from a dashboard. Fetch from IPC and save settings into a server
# TODO: Get user's discord token from oauth
