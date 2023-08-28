# This is going to be a set of commands where a guild owner/administrator can sign up to recieve
# notifications when the bot reaches milestones. They can set the channel and also select which 
# milestones they would like to be notified about

from ._base import Stats

from discord.ext import commands, tasks
from discord import app_commands
from discord.utils import utcnow

from json import load

import asyncpg

class SubscriptionCommands(Stats):
    # The task which will check the total_slanders file to see if a milestone has been reached
    @tasks.loop(minutes=1)
    async def milestone_check(self):
        # TODO:
        # Check data total type
        # Open a connection into the postgres db
        # Create settings schema (./src/schema.sql)
        # Fetch settings from the database
        # Send milestone messages to each server
        # Create milestone embed, also include new emoji
        with open("./total_slander.json") as sf:
            data = load(sf)
        
        if self.slander_cache < data['total']:
            self.slander_cache = data['total']

            if self.slander_cache % 1000 == 0:
                self.conn = await asyncpg.connect(dsn=self.bot.dsn)
                guilds = await self.conn.execute(f"SELECT * IN settings WHERE milestone=TRUE AND channel_id IS NOT null")

                for guild in guilds:

        
        