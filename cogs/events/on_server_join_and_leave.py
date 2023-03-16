from ._base import Events
from utils import constants, embeds, utils
from discord.ext.commands import Cog
from discord import Guild, abc

class ServerJoinLeave(Events):
    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        ## Check if MEE6 is in the server
        ## Collate a list of bot ids found in the server
        has_mee6 = guild.get_member(constants.MEE6_ID) is not None
        if not has_mee6:
            has_mee6 = False
            ## Find the next available channel that the bot can send a message in
            for channel in guild.text_channels:
                try:
                    await channel.send(embed=embeds.MEE6Embed.mee6_not_found())
                    break
                except Exception as e:
                    utils.log(e, "ERROR")  # FIXME: Logging.  # type: ignore

        total_members = await utils.get_total_member_count(self.bot.guilds)
        channel = await self.bot.fetch_channel(constants.LOG_CHANNEL)

        if not isinstance(channel, abc.Messageable):
            return

        await channel.send(embed=embeds.MEE6Embed.server_join(guild=guild, server_count=len(self.bot.guilds), total_members=total_members, added_members=len(guild.members), has_mee6=has_mee6))


    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        total_members = await utils.get_total_member_count(self.bot.guilds)
        channel = await self.bot.fetch_channel(constants.LOG_CHANNEL)

        if not isinstance(channel, abc.Messageable):
            return

        await channel.send(embed=embeds.MEE6Embed.server_leave(guild=guild, server_count=len(self.bot.guilds), total_members=total_members, removed_members=len(guild.members)))