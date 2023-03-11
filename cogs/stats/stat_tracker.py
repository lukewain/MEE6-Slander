from ._base import Stats
from discord.ext.commands import Cog
from discord import Message, Guild


class StatTracker(Stats):
    # Listener for message sends
    @Cog.listener()
    async def on_message(self, message: Message):
        self.msg_count += 1

        # Check if the message sent is a slander

        # Check if prefix is in message
        prefixes = self.bot.get_prefix(message)

        if (message.author.id == self.bot.user.id) and (len(prefixes) == 0):
            self.slanders_sent += 1

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
