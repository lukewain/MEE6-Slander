from __future__ import annotations

from dataclasses import dataclass
import asyncpg

__all__ = ("SlanderTarget",)

@dataclass
class SlanderTarget:
    id: int
    guild_id: int
    is_global: bool
    bot: bool
    nsfw: bool
    
    @classmethod
    def construct(cls, data: asyncpg.Record) -> SlanderTarget:
        return cls(**data)