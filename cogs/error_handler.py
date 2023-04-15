import discord
import traceback
import sys
from discord.ext import commands


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """Event is triggered when an error is raised while invoking a command.

        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation
        error: commands.CommandError
            The Exception raised.
        """

        # Prevent commands with local handlers from being handled
        if hasattr(ctx.command, "on_error"):
            return

        # Prevents any cogs with overwritten cog_command_error from being handled
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Anything in ignored will return and prevent anything happening
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.NotOwner):
            return await ctx.author.send(
                embed=discord.Embed(
                    title="Whoops",
                    description="You are not the owner. You cannot do that.",
                    colour=discord.Colour.red(),
                )
            )


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
