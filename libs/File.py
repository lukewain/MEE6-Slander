import os
import utils


class File:
    def __init__(self, path: str, parent: str):
        self.path = path
        self.parent = parent
        self.stats = os.stat(path)

    def refresh(self):
        temp_stats = os.stat(self.path)
        if temp_stats.st_mtime > self.stats.st_mtime:
            utils.debug(f"{self.path} has been modified")
            self.stats = temp_stats
