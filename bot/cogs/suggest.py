from prisma import Prisma, models
import discord
from discord import app_commands
from discord.ext import commands, tasks

from src.bot import MEE6Slander


class Suggestions(commands.Cog):
    def __init__(self, bot: MEE6Slander):
        self.bot: MEE6Slander = bot

    async def interaction_check(self, interaction: discord.Interaction[MEE6Slander]):
        # Check if the user is in the blacklist db
        res: models.BlackList | None = await interaction.client.prisma.blacklist.find_unique(where={"id": interaction.user.id})

        if not res:
            return True

        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Whoops", description="You do not have permission to do that!"
            )
        )

    @app_commands.command(name="suggest")
    async def suggest_slander(
        self,
        interaction: discord.Interaction[MEE6Slander],
        slander: app_commands.Range[str, 15, 300],
    ):
        """
        Suggests a slander to the bot moderators.

        Parameters
        ----------
        slander: str
            The slander to suggest. (up to 300 characters)
        """
        await interaction.client.slander_manager.enqueue_slander(
            slander, requester=interaction.user, bot=interaction.client
        )

        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Slander suggested.",
            description="Your slander has been successfully added to the queue. Our team will review it as soon as possible.",
        )
        embed.add_field(name="Your slander:", value=slander)

        await interaction.response.send_message(embed=embed)


async def setup(bot: MEE6Slander):
    await bot.add_cog(Suggestions(bot))
