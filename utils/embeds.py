from .emojis import Emoji
from discord import Embed, Guild, Color, Member, User
from discord.utils import utcnow


class MEE6Embed(Embed):
    @staticmethod
    def info(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.info.url)
        return embed

    @staticmethod
    def error(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.error.url)
        return embed

    @staticmethod
    def warn(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.warn.url)
        return embed

    @staticmethod
    def success(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.success.url)
        return embed

    @staticmethod
    def server_join(
        guild: Guild,
        server_count: int,
        total_members: int,
        added_members: int,
        has_mee6: bool,
    ):
        embed = Embed(title=f"Joined Server!", colour=Color.green())
        embed.add_field(name="Server Name", value=f"{guild.name}", inline=False)
        embed.add_field(name="Total Servers", value=f"{server_count}")
        embed.add_field(name="Server Owner", value=f"{guild.owner_id}", inline=False)
        embed.add_field(name="Server ID", value=f"{guild.id}")
        embed.add_field(name="Total Members", value=f"{total_members}", inline=False)
        embed.add_field(name="Added Members", value=f"+{added_members}")
        embed.add_field(
            name="Has MEE6",
            value=f"```diff\n{'+ Has MEE6' if has_mee6 else '- Does not have MEE6'}\n```",
        )
        embed.set_footer(text=utcnow())
        return embed

    @staticmethod
    def server_leave(
        guild: Guild, server_count: int, total_members: int, removed_members: int
    ):
        embed = Embed(title=f"Left Server!", colour=Color.red())
        embed.add_field(name="Server Name", value=f"{guild.name}", inline=False)
        embed.add_field(name="Total Servers", value=f"{server_count}")
        embed.add_field(name="Server Owner", value=f"{guild.owner_id}", inline=False)
        embed.add_field(name="Server ID", value=f"{guild.id}")
        embed.add_field(name="Total Members", value=f"{total_members}", inline=False)
        embed.add_field(name="Removed Members", value=f"-{removed_members}")
        embed.set_footer(text=utcnow())
        return embed

    @staticmethod
    def mee6_not_found():
        embed = Embed(
            description="Woah, MEE6 isn't in your server\nThis means that I will not work correctly!\nPlease invite MEE6 using https://MEE6.xyz"
        )
        embed.set_author(name="MEE6 not found!", icon_url=Emoji.warn.url)
        return embed

    @staticmethod
    def stats_embed(
        sent,
        all_time,
        deleted,
        edited,
        joined,
        left,
        total_servers,
        slandered,
        started,
        icon_url,
        text_cmds,
        app_cmds,
    ):
        embed = Embed(
            description=f"Stats from the bot since <t:{started}:F>", color=Color.gold()
        )
        embed.set_author(name="Stats", icon_url=icon_url)

        fields = {  # All values are assumed to be numeric such that comma formatting will work.
            "Messages Seen": sent,
            "All Time Messages Seen": all_time,
            "Messages Deleted": deleted,
            "Messages Edited": edited,
            "Servers Joined": joined,
            "Servers Left": left,
            "Total Servers": total_servers,
            "Times Slandered": slandered,
            "Text Commands Used": text_cmds,
            "/ Commands Used": app_cmds,
        }

        for name, value in fields.items():
            embed.add_field(name=name, value=f"{value:,}", inline=False)

        return embed
