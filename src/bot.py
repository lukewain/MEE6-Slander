from discord.ext.commands import Bot
from discord import Intents, AllowedMentions
from discord.utils import setup_logging

from logging import INFO
from asyncpg import create_pool
from os import environ
from dotenv import load_dotenv

import utils

load_dotenv()


class MEE6Slander(Bot):
    def __init__(self):
        # Define the bot's intents
        intents = Intents().default()
        intents.message_content = True

        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

        super().__init__(
            command_prefix="s.", intents=intents, allowed_mentions=allowed_mentions
        )

        setup_logging(level=INFO)

        self.token = environ["TOKEN"]

        self.github: str = "https://github.com/mee6-slander"
        try:
            self.pool = create_pool(
                user=environ["DB_USER"],
                host=environ["DB_HOST"],
                password=environ["DB_PASSWORD"],
            )
        except Exception as e:
            utils.log(e, "ERROR")

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")

    async def on_ready(self) -> None:
        utils.log(f"Logged in as {self.user}")
