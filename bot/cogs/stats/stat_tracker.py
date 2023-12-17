from ._base import Stats
from discord.ext.commands import Cog
from discord import Message, Guild


class StatTracker(Stats):
    # Listener for message sends
    @Cog.listener()
    async def on_message(self, message: Message):
        self.msg_count += 1

        # Allow all time messages
        await self.bot.pool.execute("UPDATE counters SET cvalue=cvalue + 1 WHERE cname='message_count'")

    # Listen for message delete
    @Cog.listener()
    async def on_message_delete(self, message: Message):
        self.del_count += 1

    # Listen for message edits
    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        self.edit_count += 1

    # Listen for server joins
    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        self.servers_joined += 1

    # Listen for server leaves
    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        self.servers_left += 1

    @Cog.listener()
    async def on_slander(self):
        self.slanders_sent += 1

    @Cog.listener()
    async def on_app_command_used(self):
        self.app_commands += 1

    @Cog.listener()
    async def on_command(self, command):
        self.text_commands += 1
