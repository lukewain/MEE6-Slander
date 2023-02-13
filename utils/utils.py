from discord.utils import utcnow


def log(text: str, type: str = "INFO") -> None:
    print(f"[{type}] {utcnow()} | {text}")
