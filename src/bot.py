from discord.ext.commands import Bot
from discord import Intents, AllowedMentions, Status, Game
from discord.utils import setup_logging

from logging import INFO
from asyncpg import create_pool
from os import environ, getcwd
from dotenv import load_dotenv
import asyncpg

from json import load, dump


import utils

load_dotenv()


class MEE6Slander(Bot):
    def __init__(self, *, pool: asyncpg.pool.Pool):
        # Define the bot's intents
        intents = Intents().default()
        intents.message_content = True
        intents.members = True

        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

        super().__init__(
            command_prefix="s.", intents=intents, allowed_mentions=allowed_mentions
        )

        setup_logging(level=INFO)

        self.token = environ["TOKEN"]

        self.github: str = "https://github.com/MEE6-Slander"

        self.admins: list = []

        with open("./config/admin.json") as adminfile:
            t = load(adminfile)

        for a in t["admins"]:
            if a not in self.admins:
                self.admins.append(a)

        # Create the asyncpg pool connection
        self.pool: asyncpg.pool.Pool = pool

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        await self.load_extension("cogs.events")

        with open("total_slander.json") as f:
            data = load(f)
            self.total = data["total"]

        await utils.parse_schema("./src/schema.sql", self.pool)
        utils.log("Schem successfully uploaded")

    async def on_ready(self) -> None:
        utils.log(f"Logged in as {self.user}")
        await self.change_presence(
            status=Status.online,
            activity=Game(name=f"Slandered MEE6 {self.total} times!"),
        )
