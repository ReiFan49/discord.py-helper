from typing import Optional
from datetime import datetime, timedelta
import asyncio
import logging

from discord.ext.commands import Bot, Cog, command, check

from ..modules import utils

log = logging.getLogger(__name__)

class Feature(Cog, name='Discord Sync'):
  '''
  Discord Application Command Sync.
  '''

  def __init__(self, bot: Bot):
    self.bot = bot
    self.daily_sync = bot.loop.create_task(self.__timed_sync(), name='bloom-jewel:daily-synchronize')

  @command(name='sync')
  @check(utils.is_owner)
  async def __sync_commands(self, ctx, *, key: Optional[str] = None) -> None:
    serverID = None
    if key == 'server':
      if ctx.guild is not None:
        serverID = ctx.guild.id
      return
    log.info('Syncing Commands on %s', 'Global' if serverID is None else serverID)
    for c in self.bot.tree.get_commands(guild=serverID):
      log.debug('- %r', repr(c))
      if hasattr(c, 'commands'):
        for cc in c.commands:
          log.debug('  - %r', repr(cc))
    await self.bot.tree.sync(guild=serverID)

  @__sync_commands.error
  async def __sync_commands_error(ctx, error):
    log.error('Command syncing error.', exc_info=error)

  async def __timed_sync(self):
    await self.bot.wait_until_ready()
    while True:
      ctime = datetime.fromtimestamp(self.bot.loop.time())
      ntime = (ctime + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0,
      )
      dtime = (ntime - ctime).total_seconds()
      await asyncio.sleep(dtime)
      if self.bot.is_closed():
        break
      try:
        await self.bot.tree.sync(guild=None)
        for serverID in self.bot.tree._guild_commands:
          await self.bot.tree.sync(guild=serverID)
      except Exception:
        log.exception('Daily command syncing error.')
