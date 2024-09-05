import os
from typing import List
import asyncio
import logging

from discord.ext.commands import (
  Bot, Cog,
)

from .. import modules
# from ..modules import utils

log = logging.getLogger(__name__)
FILE_POLLING_TIME = 10

class File(Cog,name='File Watcher'):
  '''
  Watch file based on mtime.
  '''

  def __init__(self, bot: Bot, files: List[str]):
    self.bot = bot
    self.files = files
    self.file_mtimes = dict((file, self.__obtain_file_mtime(file)) for file in files)
    self.bg_task = bot.loop.create_task(self.__watch_files(), name='bloom-jewel:file-watcher')
    self.bg_task.add_done_callback(modules.asyncio.exit_on_fail)

  async def __watch_files(self) -> None:
    while True:
      await asyncio.sleep(FILE_POLLING_TIME)
      for file in self.files:
        new_mtime = self.__obtain_file_mtime(file)
        if new_mtime == self.file_mtimes[file]:
          continue
        log.info('File %s is changed', file)
        self.bot.dispatch('c/file_change', file)
        self.file_mtimes[file] = new_mtime

  def __obtain_file_mtime(self, file: str) -> float:
    return os.stat(file).st_mtime
