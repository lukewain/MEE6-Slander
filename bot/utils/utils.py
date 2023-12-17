from discord.utils import utcnow
from discord import Guild
from asyncpg.pool import Pool

from dataclasses import dataclass
from json import load


def log(text: str, type: str = "INFO") -> None:
    print(f"[{type}] {utcnow()} | {text}")


def debug(text: str, type: str = "WARN") -> None:
    with open(f"logs/debug.log", "a") as log:
        log.write(f"[{type}] {utcnow()} | {text}\n")


def error(text: str) -> None:
    with open(f"logs/errors.log", "a") as log:
        log.write(f"[ERROR] {utcnow()} | {text}\n")


async def get_total_member_count(guilds):
    g: Guild
    total_members: int = 0
    for g in guilds:
        for member in g.members:
            if member.bot:
                pass
            else:
                total_members += 1

    return total_members


@dataclass
class Config:
    token: str
    dev_token: str | None
    pg_dsn: str
    dev_dsn: str | None
    queue_cid: int
    anyone_can_click: bool
    show_support_link: bool
    developer_mode: bool
    webhook_url: str
    join_leave_webhook: str
    prefix: str
    developer_prefix: str | None

    @classmethod
    def load_config(cls):
        with open("config.json") as f:
            data = load(f)

        return cls(**data)
