# TODO:  Store and manage whether a guild is NSFW or not.
# MAYBE TODO: Make a `Slander` class and a `State` class to handle state things.


from __future__ import annotations

import collections
import logging
import random
from typing import Deque, Dict, Tuple, Set, TypeAlias, NamedTuple
import typing
from prisma import Prisma, models, errors
import discord
from discord.ext import commands
from discord.utils import MISSING

from .helpers import *

__all__: Tuple[str, ...] = (
    "SlanderManager",
    "SlanderManagerError",
    "NoSlanderQueue",
    "SlanderAlreadyExists",
)

GuildID: TypeAlias = int
UserID: TypeAlias = int
SlanderID: TypeAlias = int

log = logging.getLogger("SlanderManager")


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


class UserConfig(NamedTuple):
    """Container to access settings for a user."""

    nsfw: bool


class SlanderManagerError(Exception):
    """Base exception for the slander manager."""


class NoSlanderQueue(Exception):
    def __init__(self) -> None:
        super().__init__("No slander channel was found.")


class SlanderAlreadyExists(discord.ClientException):
    def __init__(self) -> None:
        super().__init__("That slander already exists.")


class InvalidExecuteLocation(Exception):
    def __init__(self) -> None:
        super().__init__("This command can only be run from a guild.")


class UserDMNotOpen(Exception):
    def __init__(self, user: discord.User) -> None:
        super().__init__(f"{user} does not have their DM's opened.")


class QueueView(discord.ui.View):
    def __init__(self, *, slander_id: int, manager: SlanderManager):
        super().__init__(timeout=None)
        self.manager = manager
        self.slander_id = slander_id
        self.approve.custom_id = str(self.approve.custom_id).format(slander_id)
        self.approve_nsfw.custom_id = str(self.approve_nsfw.custom_id).format(
            slander_id
        )
        self.reject.custom_id = str(self.reject.custom_id).format(slander_id)

    async def interaction_check(
        self, interaction: discord.Interaction[commands.Bot], /
    ) -> bool:
        if self.manager._no_view_check:
            return True
        if await interaction.client.is_owner(interaction.user):
            return True
        await interaction.response.send_message("You cannot do that.", ephemeral=True)
        return False

    async def send_notification(self, interaction: discord.Interaction, slander_id):
        # Fetch slander content
        res: models.Slander = await interaction.client.prisma.slander.find_unique(where={"id": slander_id}) # type: ignore

        embed = discord.Embed(description=res.message)
        if res.nsfw and res.approved:
            embed.title = f"Slander Accepted (NSFW) by {interaction.user}"
            embed.color = discord.Colour.orange()
        elif res.approved:
            embed.title = f"Slander Accepted by {interaction.user}"
            embed.color = discord.Colour.green()
        else:
            embed.title = f"Slander Denied by {interaction.user}"
            embed.color = discord.Colour.red()

        # Fetch the user
        creator_obj: discord.User | None = interaction.client.get_user(res.creator)

        if creator_obj:
            try:
                await creator_obj.send(embed=embed)
            except discord.errors.Forbidden:
                raise UserDMNotOpen(creator_obj)

    @discord.ui.button(
        label="approve",
        custom_id="Slanders::approve::{}",
        style=discord.ButtonStyle.green,
    )
    async def approve(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not interaction.message:
            return await interaction.response.send_message(
                "Something went wrong... `Interaction.message` was `None`",
                ephemeral=True,
            )
        if not interaction.message.embeds:
            return await interaction.response.send_message(
                "Something went wrong... `Interaction.message.embeds` was empty.",
                ephemeral=True,
            )
        success = await self.manager.update_slander(
            self.slander_id, approved=True, nsfw=False
        )
        if not success:
            return await interaction.response.send_message(
                "Failed to update this slander. Was it deleted?", ephemeral=True
            )

        embed = interaction.message.embeds[0]
        embed.set_footer(text="Slander approved.")
        embed.colour = discord.Colour.green()
        await interaction.response.edit_message(embed=embed, view=None)
        await self.send_notification(interaction, self.slander_id)
        self.stop()

    @discord.ui.button(
        label="approve (nsfw)",
        custom_id="Slanders::nsfw::{}",
        style=discord.ButtonStyle.blurple,
    )
    async def approve_nsfw(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not interaction.message:
            return await interaction.response.send_message(
                "Something went wrong... `Interaction.message` was `None`",
                ephemeral=True,
            )
        if not interaction.message.embeds:
            return await interaction.response.send_message(
                "Something went wrong... `Interaction.message.embeds` was empty.",
                ephemeral=True,
            )
        success = await self.manager.update_slander(
            self.slander_id, approved=True, nsfw=True
        )
        if not success:
            return await interaction.response.send_message(
                "Failed to update this slander. Was it deleted?", ephemeral=True
            )

        embed = interaction.message.embeds[0]
        embed.set_footer(text="Slander approved as NSFW.")
        embed.colour = discord.Colour.dark_green()
        await interaction.response.edit_message(embed=embed, view=None)
        await self.send_notification(interaction, self.slander_id)
        self.stop()

    @discord.ui.button(
        label="deny", custom_id="Slanders::reject::{}", style=discord.ButtonStyle.red
    )
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.message:
            return await interaction.response.send_message(
                "Something went wrong... `Interaction.message` was `None`",
                ephemeral=True,
            )
        if not interaction.message.embeds:
            return await interaction.response.send_message(
                "Something went wrong... `Interaction.message.embeds` was empty.",
                ephemeral=True,
            )

        success = await self.manager.update_slander(self.slander_id, approved=False)
        if not success:
            return await interaction.response.send_message(
                "Failed to update this slander. Was it deleted?", ephemeral=True
            )

        embed = interaction.message.embeds[0]
        embed.set_footer(text="Slander denied.")
        embed.colour = discord.Colour.red()
        await interaction.response.edit_message(embed=embed, view=None)
        await self.send_notification(interaction, self.slander_id)
        self.stop()


class SlanderManager:
    def __init__(
        self,
        prisma: Prisma,
        queue_channel_id: int,
        anyone_can_click: bool,
    ) -> None:
        self._prisma: Prisma = prisma
        self._channel_id: int = queue_channel_id
        self._no_view_check: bool = anyone_can_click

        self._safe_slanders: Dict[SlanderID, str] = {}
        self._all_slanders: Dict[SlanderID, str] = {}
        self._user_slanders: Dict[SlanderID, str] = {}
        self._safe_user_slanders: Dict[SlanderID, str] = {}
        self._slander_queues: Dict[GuildID | UserID, Deque[int]] = {}
        self._nsfw_guilds: Set[GuildID] = set()
        self._nsfw_users: Set[UserID] = set()

        self.started: bool = False

    async def __aenter__(self):
        try:
            await self.start()
        except Exception as e:
            log.error("Could not start slander manager's cache.", exc_info=e)

        return self

    async def __aexit__(self, *_):
        pass

    async def start(self):
        """Caches all the slanders."""
        slanders: list[models.Slander] = await self._prisma.slander.find_many(where={"approved": {"equals": True}})
        self._all_slanders = dict(slanders)  # type: ignore  # Yes you can be dict()'d.

        safe_slanders: list[models.Slander] = await self._prisma.slander.find_many(where={"approved": {"equals": True}, "nsfw": {"equals": False}})
        self._safe_slanders = dict(safe_slanders)  # type: ignore  # Yes you can be dict()'d.
        
        # ! Unused currently
        # ! Waiting to be implemented
        # query: str = (
        #     "SELECT id, message FROM slanders WHERE approved = TRUE AND is_user = TRUE;"
        # )
        # user_slanders: list[models.Slander] = await self._pool.fetch(query)
        # self._user_slanders = dict(user_slanders)  # type: ignore   # Yes you can be dict()'d.
        # query: str = "SELECT id, message FROM slanders WHERE approved = TRUE AND nsfw = FALSE AND is_user = TRUE;"
        # safe_user_slanders: list[asyncpg.Record] = await self._pool.fetch(query)
        # self._safe_user_slanders = dict(safe_user_slanders)  # type: ignore   # Yes you can be dict()'d.

        """Caches all the guilds and users"""
        guilds: list[models.Guild] = await self._prisma.guild.find_many(where={"nsfw": {"equals": True}, "added": {"not": None}})
        guild_ids: list[int] = [GuildID(guild.id) for guild in guilds]
        self._nsfw_guilds.update(guild_ids)

        # ! Unused currently
        # ! Unknown if this is actually needed
        # query: str = "SELECT id FROM alt_slander WHERE nsfw = TRUE;"
        # users: list[asyncpg.Record] = await self._pool.fetch(query)
        # user_ids: list[int] = [UserID(user["id"]) for user in users]
        # self._nsfw_users.update(user_ids)
        # self.started = True

        """Cache all the global slander target ids"""
        global_targets: list[models.SlanderTarget] = await self._prisma.slandertarget.find_many(where={"is_global": {"equals": True}})
        self._global_targets = global_targets

    async def register_views(self, client: commands.Bot):
        query: str = "SELECT ARRAY(SELECT id FROM slanders WHERE approved ISNULL);"
        unapproved_slanders: list[models.Slander] = await self._prisma.slander.find_many(where={"approved": {"equals": None}})
        slander_ids: list[int] = [slander.id for slander in unapproved_slanders]
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
        channel = bot.get_channel(self._channel_id)
        if not isinstance(channel, discord.TextChannel):
            raise NoSlanderQueue
        user_friendly = "mee6" in slander.lower()
        try:
            slander_id: int = await self._prisma.slander.create(data={"message": slander, "creator": requester.id, "is_user": user_friendly}, include={"id": True})
        except errors.UniqueViolationError as e:
            raise SlanderAlreadyExists from e

        embed = discord.Embed(
            title=f"Slander request from {requester}",
            description=slander,
            color=discord.Color.blurple(),
        )

        await channel.send(
            embed=embed, view=QueueView(slander_id=slander_id, manager=self)
        )

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

        if approved is MISSING and nsfw is MISSING:
            return False

        data = {}

        if approved is not MISSING:
            data['approved'] = approved

        if nsfw is not MISSING:
            data['nsfw'] = nsfw

        row = await self._prisma.slander.find_unique(where={"id": slander_id})

        if row:
            if nsfw is MISSING:
                nsfw = row.nsfw
            if approved is MISSING:
                approved = row.approved

            if approved:
                self._all_slanders[slander_id] = row.message
                if nsfw:
                    self._safe_slanders.pop(slander_id, None)
                else:
                    self._safe_slanders[slander_id] = row.message
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

        result = await self._prisma.slander.delete(where={"id": slander_id})

        self._remove_slander_from_queues(slander_id)

        return len(result) == 1

    async def process_message(self, message: discord.Message):
        if message.author.id in self._global_targets:
            return await message.reply(
                self.get_slander(message.guild.id, message.author.id)
            )

        query = "SELECT * FROM slander_targets WHERE id=$1 AND guild_id=$2"
        db_resp: list[models.SlanderTarget] = await self._prisma.slandertarget.find_first(where={"id": message.author.id, "guild_id": message.guild.id})

        # Format them into SlanderTarget's
        if len(db_resp) == 0:
            return
        slander_target_list = [SlanderTarget.construct(entry) for entry in db_resp]

    def get_slander(
        self,
        guild: typing.Optional[discord.Guild] = None,
        user: typing.Optional[typing.Union[discord.Member, discord.User]] = None,
    ) -> str:  # type: ignore    # Can be ignored due to one always being included
        """
        Gets a slander from the guild's or user's queue. If there's no queue or if it
        has been exhausted, it creates a new randomly shuffled queue.

        Parameter
        ---------
        guild: discord.Guild | None
            The guild to use to get the queue.

        user: discord.User | discord.Member | None
            The user to get a queue for.

        Returns
        -------
        str
            A slander that's not been used before.
        """
        if guild:
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

        elif user:
            try:
                slander_id = self._slander_queues[user.id].pop()
            except (KeyError, IndexError):
                if user.id in self._nsfw_users:
                    slanders = list(self._user_slanders.keys())
                else:
                    slanders = list(self._safe_user_slanders.keys())
                random.shuffle(slanders)

                *slanders, slander_id = slanders
                self._slander_queues[user.id] = collections.deque(slanders)

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

    def get_user_config(self, user: discord.User | discord.Member) -> UserConfig:
        """Gets the current settings for the user.

        Parameters
        __________
        user: discord.User | discord.Member
            The user to get the config for

        Returns
        _______
        UserConfig
            The current settings for the user
        """
        return UserConfig(nsfw=user.id in self._nsfw_users)

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
        await self._prisma.guild.upsert(where={"id": guild.id}, data={"nsfw": nsfw})
        if nsfw:
            self._nsfw_guilds.add(guild.id)
        else:
            self._nsfw_guilds.discard(guild.id)

    async def update_user(
        self, user: discord.Member, /, *, nsfw: typing.Optional[bool]
    ):
        """
        Updates the settings of a user.

        Inherits from the guild's nsfw settings

        Parameters
        ----------
        user: discord.User | discord.Member
            The user to update
        nsfw: Optional[bool]
            If specified will override the guild config
        """

        if not user.guild:
            raise InvalidExecuteLocation

        # if bool:
        #     # Overrides the guild config
        #     is_nsfw = await self._prisma.alt_slander.fetchval(
        #         "UPDATE alt_slander SET nsfw=$1 WHERE id=$2 AND guild_id=$3",
        #         nsfw,
        #         user.id,
        #         user.guild.id,
        #     )

        else:
            # Fetch the guild config
            guild_nsfw = await self._prisma.guild.find_first(where={"id": user.guild.id}, include={"nsfw": True})

    async def register_new_slander_target(
        self,
        user: discord.Member,
        guild_id: typing.Optinal[int],
        is_global: typing.Optional[bool],
    ) -> bool:
        # Check if the target will be global
        query = "SELECT * FROM slander_targets WHERE id = $1"
        res: list[models.SlanderTarget] = await self._prisma.slandertarget.find_first(where={"id": user.id})

        if len(res) > 0:
            pre_existing = [SlanderTarget.construct(data) for data in res]
        else:
            pre_existing = []

    def __repr__(self) -> str:
        cls = type(self)
        return f"<{cls.__module__}.{cls.__name__} with queue at {self._channel_id}, with {len(self._all_slanders)} guild slanders, {len(self._user_slanders)} user slanders and {len(self._slander_queues)} active queues>"
