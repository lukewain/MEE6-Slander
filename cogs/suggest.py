import asyncpg
import discord
from discord import app_commands
from discord.ext import commands, tasks

from src.bot import MEE6Slander


class Suggestions(commands.Cog):
    def __init__(self, bot: MEE6Slander):
        self.bot: MEE6Slander = bot

    async def cog_load(self):
        self.slander_request_update.start()

    @app_commands.command(name='suggest')
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
        await interaction.client.slander_manager.enqueue_slander(slander, requester=interaction.user, bot=interaction.client)

        embed = discord.Embed(
            color=discord.Color.blurple(),
            title='Slander suggested.',
            description='Your slander has been successfully added to the queue. Our team will review it as soon as possible.',
        )
        embed.add_field(name='Your slander:', value=slander)

        await interaction.response.send_message(embed=embed)

    # Task to alert the user on the status of their slander suggestion
    @tasks.loop(minutes=10)
    async def slander_request_update(self):
        # Fetch the slanders from the database where notified is false and approved is not null
        query: str = "SELECT * FROM slanders WHERE notified=False AND approved IS NOT NULL"

        res: list[asyncpg.Record] = await self.bot.pool.fetch(query)

        # loop through the records returned

        for record in res:
            embed = discord.Embed(description=record['message'])
            match record['approved']:
                case True:
                    embed.colour = discord.Colour.green()
                    embed.title = "Slander Accepted!"
                case False:
                    embed.colour = discord.Colour.red()
                    embed.title = "Slander Denied!"
                
            if record['approved'] and record['nsfw']:
                embed.add_field(name="NSFW", value="The slander has been marked as NSFW")
            
            usr: discord.User | None = self.bot.get_user(record['creator'])

            if not usr:
                await self.bot._log_webhook.send(embed=discord.Embed(title="An error occured", description=f"The user {record['creator']} was not found", colour=discord.Colour.red()))
            else:
                try:
                    await usr.send(embed=embed)
                except discord.HTTPException as e:
                    await self.bot._log_webhook.send(embed=discord.Embed(title="User DM Error", description=e, colour=discord.Colour.red()))

            # Update the record to say that the user has been notified
            query: str = "UPDATE slanders SET notified=True WHERE id=$1"

            await self.bot.pool.execute(query, record['id'])


    # Wait until the bot is ready
    @slander_request_update.before_loop
    async def before_bot_ready(self):
        await self.bot.wait_until_ready()


async def setup(bot: MEE6Slander):
    await bot.add_cog(Suggestions(bot))
