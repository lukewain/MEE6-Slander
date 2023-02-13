import os
import time


class Directory:
    def __init__(self, path: str, watch: bool = True):
        self.path = path
        self.cache = []
        self.last_updated: int = 0

    def walk(self, path: str = None):
        p = path or self.path
        for file in os.listdir(p):
            if os.path.isdir(file):
                self.walk(file)
