from .emojis import Emoji
from discord import Embed, Guild, Color, Member, User
from discord.utils import utcnow


class MEE6Embed(Embed):
    def info(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.info.url)
        return embed

    def error(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.error.url)
        return embed

    def warn(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.warn.url)
        return embed

    def success(title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.success.url)
        return embed

    def server_join(guild: Guild, server_count: int, total_members: int, added_members: int, has_mee6: bool):
        embed = Embed(title=f"Joined Server!", colour=Color.green())
        embed.add_field(name="Server Name", value=f"{guild.name}", inline=False)
        embed.add_field(name="Total Servers", value=f"{server_count}")
        embed.add_field(name="Server Owner", value=f"{guild.owner_id}", inline=False)
        embed.add_field(name="Server ID", value=f"{guild.id}")
        embed.add_field(name="Total Members", value=f"{total_members}", inline=False)
        embed.add_field(name="Added Members", value=f"+{added_members}")
        embed.add_field(name="Has MEE6", value=f"```diff\n{'+ Has MEE6' if has_mee6 else '- Does not have MEE6'}\n```")
        embed.set_footer(text=utcnow())
        return embed

    def server_leave(guild: Guild, server_count: int, total_members: int, removed_members: int):
        embed = Embed(title=f"Left Server!", colour=Color.red())
        embed.add_field(name="Server Name", value=f"{guild.name}", inline=False)
        embed.add_field(name="Total Servers", value=f"{server_count}")
        embed.add_field(name="Server Owner", value=f"{guild.owner_id}", inline=False)
        embed.add_field(name="Server ID", value=f"{guild.id}")
        embed.add_field(name="Total Members", value=f"{total_members}", inline=False)
        embed.add_field(name="Removed Members", value=f"-{removed_members}")
        embed.set_footer(text=utcnow())
        return embed
    
    def mee6_not_found(owner: Member):
        embed = Embed(description="Woah, MEE6 isn't in your server\nThis means that I will not work correctly!\nPlease invite MEE6 using https://MEE6.xyz")
        embed.set_author(name="MEE6 not found!", icon_url=Emoji.warn.url)
        return embed