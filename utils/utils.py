from discord.utils import utcnow
from discord import Guild
from asyncpg.pool import Pool


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

async def parse_schema(schema_path: str, pool: Pool) -> bool:
    with open(schema_path) as schema_file:
        data = schema_file.readlines()

    async with pool.acquire() as conn:
        # Loop through schema lines
        ret = []
        for line in data:
            ret.append(line)
            if ';' in line:
                query = ''.join(ret)
                if query.strip():
                    await conn.execute(query)
                ret = []

        if ret:
                query = ''.join(ret)
                if query.strip():
                    await conn.execute(query)
                await conn.commit()
            
    
