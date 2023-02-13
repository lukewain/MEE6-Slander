from .emojis import Emoji
from discord import Embed


class MEE6Embed(Embed):
    def info(cls, title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.info.url)
        return embed

    def error(cls, title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.error.url)
        return embed

    def warn(cls, title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.warn.url)
        return embed

    def success(cls, title: str, description: str):
        embed = Embed(description=description)
        embed.set_author(name=title, icon_url=Emoji.success.url)
