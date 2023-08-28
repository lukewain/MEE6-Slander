import discord
from discord.ext import commands

import pygit2
import itertools
import datetime

from ._base import Information


def format_commit(commit):
    short, _, _ = commit.message.partition("\n")
    short = short[0:40] + "..." if len(short) > 40 else short
    short_sha2 = commit.hex[0:6]
    commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
    commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)
    offset = discord.utils.format_dt(commit_time, style="R")
    return f"[`{short_sha2}`](https://github.com/lukewain/MEE6-Slander/commit/{commit.hex}) {short} ({offset})"


def get_latest_commits(limit: int = 5):
    repo = pygit2.Repository("./.git")
    commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), limit))
    return "\n".join(format_commit(c) for c in commits)


class Github(Information):
    @commands.group(invoke_without_command=True)
    async def infomation(self, ctx: commands.Context)