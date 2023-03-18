# TODO:  Store and manage wether a guild is NSFW or not.
# MAYBE TODO: Make a `Slander` class and a `State` class to handle state things.


from __future__ import annotations

import collections
import logging
import random
from typing import Deque, Dict, Tuple, Set, TypeAlias, NamedTuple

import asyncpg
import discord
from discord.ext import commands
from discord.utils import MISSING

__all__: Tuple[str, ...] = ("SlanderManager", "SlanderManagerError", "NoSlanderQueue", "SlanderAlreadyExists")

GuildID: TypeAlias = int
SlanderID: TypeAlias = int

log = logging.getLogger('SlanderManager')


class PGSafeDict(dict):
    """
    A dict for formatting PostgreSQL queries safely.

    Example usage:

    .. code-block:: python3

        query = "SELECT thing FROM table WHERE x={foo} and y={bar}"
        args = PGSafeDict({'foo': 1, 'bar': 2})

        print(query.format_map(args))  # "SELECT thing FROM table WHERE x=$1 AND y=$2"

        await connection.execute(query.format_map(args), *args.values())
    """

    def __getitem__(self, __key: str):
        return f"${list(self.keys()).index(__key) + 1}"


class GuildConfig(NamedTuple):
    """Container to access settings for a guild."""

    nsfw: bool


class SlanderManagerError(Exception):
    """Base exception for the slander manager."""


class NoSlanderQueue(Exception):
    def __init__(self) -> None:
        super().__init__("No slander channel was found.")


class SlanderAlreadyExists(discord.ClientException):
    def __init__(self) -> None:
        super().__init__("That slander already exists.")


class QueueView(discord.ui.View):
    def __init__(self, *, slander_id: int, manager: SlanderManager):
        super().__init__(timeout=None)
        self.manager = manager
        self.slander_id = slander_id
        self.approve.custom_id = str(self.approve.custom_id).format(slander_id)
        self.approve_nsfw.custom_id = str(self.approve_nsfw.custom_id).format(slander_id)
        self.reject.custom_id = str(self.reject.custom_id).format(slander_id)

    async def interaction_check(self, interaction: discord.Interaction[commands.Bot], /) -> bool:
        if self.manager._no_view_check:
            return True
        if await interaction.client.is_owner(interaction.user):
            return True
        await interaction.response.send_message('You cannot do that.', ephemeral=True)
        return False

    @discord.ui.button(label='approve', custom_id='Slanders::approve::{}', style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.message:
            return await interaction.response.send_message(
                'Something went wrong... `Interaction.message` was `None`', ephemeral=True
            )
        if not interaction.message.embeds:
            return await interaction.response.send_message(
                'Something went wrong... `Interaction.message.embeds` was empty.', ephemeral=True
            )
        success = await self.manager.update_slander(self.slander_id, approved=True, nsfw=False)
        if not success:
            return await interaction.response.send_message("Failed to update this slander. Was it deleted?", ephemeral=True)

        embed = interaction.message.embeds[0]
        embed.set_footer(text='Slander approved.')
        embed.colour = discord.Colour.green()
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label='approve (nsfw)', custom_id='Slanders::nsfw::{}', style=discord.ButtonStyle.blurple)
    async def approve_nsfw(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.message:
            return await interaction.response.send_message(
                'Something went wrong... `Interaction.message` was `None`', ephemeral=True
            )
        if not interaction.message.embeds:
            return await interaction.response.send_message(
                'Something went wrong... `Interaction.message.embeds` was empty.', ephemeral=True
            )
        success = await self.manager.update_slander(self.slander_id, approved=True, nsfw=True)
        if not success:
            return await interaction.response.send_message("Failed to update this slander. Was it deleted?", ephemeral=True)

        embed = interaction.message.embeds[0]
        embed.set_footer(text='Slander approved as NSFW.')
        embed.colour = discord.Colour.dark_green()
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label='deny', custom_id='Slanders::reject::{}', style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.message:
            return await interaction.response.send_message(
                'Something went wrong... `Interaction.message` was `None`', ephemeral=True
            )
        if not interaction.message.embeds:
            return await interaction.response.send_message(
                'Something went wrong... `Interaction.message.embeds` was empty.', ephemeral=True
            )

        success = await self.manager.update_slander(self.slander_id, approved=False)
        if not success:
            return await interaction.response.send_message("Failed to update this slander. Was it deleted?", ephemeral=True)

        embed = interaction.message.embeds[0]
        embed.set_footer(text='Slander denied.')
        embed.colour = discord.Colour.red()
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()


class SlanderManager:
    def __init__(self, pool: asyncpg.Pool[asyncpg.Record], queue_channel_id: int, anyone_can_click: bool) -> None:
        self._pool = pool
        self._channel_id = queue_channel_id
        self._no_view_check = anyone_can_click

        self._safe_slanders: Dict[SlanderID, str] = {}
        self._all_slanders: Dict[SlanderID, str] = {}
        self._slander_queues: Dict[GuildID, Deque[int]] = {}
        self._nsfw_guilds: Set[GuildID] = set()

        self.started: bool = False

    async def __aenter__(self):
        try:
            await self.start()
        except Exception as e:
            log.error('Could not start slander manager\'s cache.', exc_info=e)

        return self

    async def __aexit__(self, *_):
        pass

    async def start(self):
        """Caches all the slanders."""
        query: str = "SELECT id, message FROM slanders WHERE approved = TRUE;"
        slanders = await self._pool.fetch(query)
        self._all_slanders = dict(slanders)  # type: ignore  # Yes you can be dict()'d.

        query: str = "SELECT id, message FROM slanders WHERE approved = TRUE AND nsfw = FALSE;"
        safe_slanders = await self._pool.fetch(query)
        self._safe_slanders = dict(safe_slanders)  # type: ignore  # Yes you can be dict()'d.
        self.started = True

    async def register_views(self, client: commands.Bot):
        query: str = "SELECT ARRAY(SELECT id FROM slanders WHERE approved ISNULL);"
        slander_ids = await self._pool.fetchval(query)
        for slander_id in slander_ids:
            client.add_view(QueueView(slander_id=slander_id, manager=self))

    def _remove_slander_from_queues(self, slander_id: int):
        for queue in self._slander_queues.values():
            try:
                queue.remove(slander_id)
            except ValueError:
                pass
        self._safe_slanders.pop(slander_id, None)
        self._all_slanders.pop(slander_id, None)

    async def enqueue_slander(
        self,
        slander: str,
        /,
        *,
        requester: discord.abc.User,
        bot: commands.Bot,
    ):
        """
        Enqueues a slander so moderators can approve or deny it.

        Parameters
        ----------
        slander: str
            The slander itself.
        requester: discord.User
            The person who requested this slander to be added.
        bot: commands.Bot
            The bot. Used to get the queue channel.

        Raises
        ------
        NoSlanderQueue
            The queue channel was not found.
        SlanderAlreadyExists
            There was already a slander with this name.
        """
        async with self._pool.acquire() as conn, conn.transaction():
            channel = bot.get_channel(self._channel_id)
            if not isinstance(channel, discord.TextChannel):
                raise NoSlanderQueue
            query: str = "INSERT INTO slanders (message, creator) VALUES ($1, $2) RETURNING id"
            try:
                slander_id: int = await conn.fetchval(query, slander, requester.id)
            except asyncpg.UniqueViolationError as e:
                raise SlanderAlreadyExists from e

            embed = discord.Embed(
                title=f'Slander request from {requester}', description=slander, color=discord.Color.blurple()
            )

            await channel.send(embed=embed, view=QueueView(slander_id=slander_id, manager=self))

    async def update_slander(
        self,
        slander_id: SlanderID,
        /,
        *,
        approved: bool | None = MISSING,
        nsfw: bool = MISSING,
    ):
        """Updates the approval and nsfw status of a slander.

        Parameters
        ----------
        slander_id: SlanderID
            The ID of the slander to update.
        approved: bool or None
            the status of the slander.

            True = Approved
            False = Denied
            None = Pending
        nsfw: bool
            Wether this slander is considered NSFW.

        Returns
        -------
        bool
            Wether the slander was successfully updated. If false, it means the slander
            was not found in the database, or no keyword-arguments were given.
        """
        asyncpg.create_pool
        if approved is MISSING and nsfw is MISSING:
            return False

        args = PGSafeDict()
        set_args: list[str] = []

        if nsfw is not MISSING:
            set_args.append('nsfw={nsfw}')
            args['nsfw'] = nsfw

        if approved is not MISSING:
            set_args.append('approved={approved}')
            args['approved'] = approved

        query = "UPDATE slanders SET " + ", ".join(set_args) + " WHERE id={id} RETURNING *"
        args['id'] = slander_id

        row = await self._pool.fetchrow(query.format_map(args), *args.values())

        if row:
            if nsfw is MISSING:
                nsfw = row['nsfw']
            if approved is MISSING:
                approved = row['approved']

            if approved:
                self._all_slanders[slander_id] = row['message']
                if nsfw:
                    self._safe_slanders.pop(slander_id, None)
                else:
                    self._safe_slanders[slander_id] = row['message']
            else:
                self._remove_slander_from_queues(slander_id)
            return True

        return False

    async def delete_slander(self, slander_id: SlanderID, /) -> bool:
        """Deletes a slander.

        Parameters
        ----------
        slander_id: SlanderID
            The ID of the slander to delete.

        Returns
        -------
        bool
            wether the slander was successfully deleted.
        """

        query: str = "DELETE FROM slanders WHERE id = $1 RETURNING *"
        result = await self._pool.fetch(query, slander_id)

        self._remove_slander_from_queues(slander_id)

        return len(result) == 1

    def get_slander(self, guild: discord.Guild) -> str:
        """
        Gets a slander from the guild's queue. If there's no queue or if it
        has been exhausted, it creates a new randomly shuffled queue.

        Parameter
        ---------
        guild: discord.Guild
            The guild to use to get the queue.

        Returns
        -------
        str
            A slander slander that's not been used before.
        """
        try:
            slander_id = self._slander_queues[guild.id].pop()
        except (KeyError, IndexError):
            # The queue was exhausted or non-existent, so we need to create a new shuffled one.
            if guild.id in self._nsfw_guilds:
                slanders = list(self._all_slanders.keys())
            else:
                slanders = list(self._safe_slanders.keys())
            random.shuffle(slanders)

            *slanders, slander_id = slanders
            self._slander_queues[guild.id] = collections.deque(slanders)

        return self._all_slanders[slander_id]

    def get_guild_config(self, guild: discord.Guild) -> GuildConfig:
        """Gets the current settings for this guild.

        Parameters
        ----------
        guild: discord.Guild
            The guild to get the config for.

        Returns
        -------
        GuildConfig
            The current settings for this guild.
        """
        return GuildConfig(
            nsfw=guild.id in self._nsfw_guilds,
        )

    async def update_guild(self, guild: discord.Guild, /, *, nsfw: bool):
        """
        Updates the settings of a guild.

        Parameters
        ----------
        guild: discord.Guild
            The guild to update.
        nsfw: bool
            Wether this guild should allow NSFW slanders.
        """
        # Note, if this requires multiple params, do something like in `self.update_slander`
        query: str = """
            INSERT INTO guilds (id, nsfw) VALUES ($1, $2)
                ON CONFLICT (id) DO UPDATE SET nsfw = $2
        """
        await self._pool.execute(query, guild.id, nsfw)
        if nsfw:
            self._nsfw_guilds.add(guild.id)
        else:
            self._nsfw_guilds.discard(guild.id)

    def __repr__(self) -> str:
        cls = type(self)
        return f"<{cls.__module__}.{cls.__name__} with queue at {self._channel_id}, with {len(self._all_slanders)} slanders and {len(self._slander_queues)} active queues>"
