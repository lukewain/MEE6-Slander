import os
from libs.File import File
import utils
import time


class Directory:
    def __init__(self, bot, path: str, watch: bool = True):
        self.bot = bot
        self.path = path
        self.cache = []
        self.last_updated: int = 0
        self.watch = watch

        self.generateCache()

    def walk(self, path: str = None):
        p = path or self.path
        for file in os.listdir(p):
            if os.path.isdir(file):
                self.walk(file)

    def generateCache(self):
        for file in os.listdir(self.path):
            if os.path.isdir(f"{self.path}\\{file}"):
                utils.debug(f"Added directory {self.path}\\{file}")
                self.bot.dirList.append(Directory(self.bot, f"{self.path}\\{file}"))

            else:
                utils.debug(f"Cached file {self.path}\\{file}")
                self.cache.append(File(f"{self.path}\\{file}", self.path))

    def updateFiles(self):
        file: File
        for file in self.cache:
            file.refresh()
