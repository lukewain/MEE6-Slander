from __future__ import annotations

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
    def __init__(self, *, pool: asyncpg.Pool[asyncpg.Record], slander_manager: utils.SlanderManager):
        # Define the bot's intents
        intents = Intents().default()
        intents.message_content = True
        intents.members = True

        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

        super().__init__(command_prefix="s.", intents=intents, allowed_mentions=allowed_mentions, tree_cls=SlanderTree)

        self.token = environ["TOKEN"]

        self.github: str = "https://github.com/MEE6-Slander"

        self.admins: list = []

        self.pool = pool
        self.slander_manager = slander_manager

        with open("./config/admin.json") as adminfile:
            t = load(adminfile)

        for a in t["admins"]:
            if a not in self.admins:
                self.admins.append(a)

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
