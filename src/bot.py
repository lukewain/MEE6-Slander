from __future__ import annotations
import os

from discord.ext.commands import Bot
from discord import Intents, AllowedMentions, Status, Game
from discord.utils import setup_logging

from os import environ
from dotenv import load_dotenv
import asyncpg

from json import load


import utils
from .tree import SlanderTree

load_dotenv()
setup_logging()


class MEE6Slander(Bot):
    def __init__(self, *, pool: asyncpg.Pool[asyncpg.Record], slander_manager: utils.SlanderManager, dev_mode: bool):
        # Define the bot's intents
        intents = Intents().default()
        intents.message_content = True
        intents.members = True

        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

        super().__init__(command_prefix="s.", intents=intents, allowed_mentions=allowed_mentions, tree_cls=SlanderTree)

        self.dev_mode = dev_mode
        self.token = environ["TOKEN"] if not dev_mode else environ['DEV_TOKEN']

        self.github: str = "https://github.com/lukewain/MEE6-Slander"

        self.support_link: str = "https://discord.gg/EQpxMZSFy3"
        self.show_support_link = os.environ["SHOW_SUPPORT_LINK"]

        self.pool = pool
        self.slander_manager = slander_manager

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.config")
        await self.load_extension("cogs.suggest")

    async def create_tables(self):
        with open("total_slander.json") as f:
            data = load(f)
            self.total = data["total"]

        with open("./src/schema.sql") as file:
            await self.pool.execute(file.read())
        utils.log("Schema successfully uploaded")

    async def on_ready(self) -> None:
        utils.log(f"Logged in as {self.user}")
        await self.change_presence(
            status=Status.online,
            activity=Game(name=f"Slandered MEE6 {self.total} times!"),
        )
