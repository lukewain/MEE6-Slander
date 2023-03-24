from ._base import Events
from .on_mee6_message import MEE6Message
from .on_server_join_and_leave import ServerJoinLeave
from .misc import MemberJoinLeave


class EventsCog(MEE6Message, ServerJoinLeave, MemberJoinLeave):
    """Events cog"""


async def setup(bot):
    await bot.add_cog(EventsCog(bot))
