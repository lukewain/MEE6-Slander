from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands

import utils

if TYPE_CHECKING:
    from .bot import MEE6Slander


class SlanderTree(app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction[MEE6Slander], error: app_commands.AppCommandError, /) -> None:
        if isinstance(error, app_commands.CommandInvokeError):
            if isinstance(error.original, utils.SlanderManagerError):
                return await interaction.response.send_message(str(error.original))
        return await super().on_error(interaction, error)
