import discord

from src.bot import MEE6Slander
from ._base import Config


class SlanderSettings(Config):
    @Config.config.command(name="nsfw")
    async def config_nsfw(self, interaction: discord.Interaction[MEE6Slander], enabled: bool):
        """
        Toggle wether to show slanders marked as NSFW.

        Parameters
        ----------
        enabled: bool
            Wether to allow or disallow NSFW slanders.
        """
        if not interaction.guild:
            return await interaction.response.send_message("This command must be executed within a server.", ephemeral=True)

        await interaction.client.slander_manager.update_guild(interaction.guild, nsfw=enabled)
        messages = ["Now omitting NSFW slanders.", "Now showing NSFW slanders."]
        await interaction.response.send_message(messages[enabled], ephemeral=True)
