#!/usr/bin/env python3
import sys
import asyncio
import logging
import argparse
from typing import Callable, Union, Type

import discord
from discord.utils import setup_logging, oauth_url
from discord.ext import commands
from discord.ext.commands import CommandNotFound

from bloom_jewel.discord_utils import plugins
from bloom_jewel.discord_utils.errors import EventInterrupt
from bloom_jewel.discord_utils.modules import config, shared

PrefixType = Union[str, Callable[[commands.Bot, discord.Message], str]]
UNDEFINED = object()

log = logging.getLogger(__name__)

class Application():
  ''' Defines application bootstrap definition. '''

  config_class : Type[config.Config] = config.Config

  def __init__(
    self,
    prefix : PrefixType = UNDEFINED,
    /,
    *,
    intents : discord.Intents = discord.Intents.default(),
    config_file : str = 'config.yml',
  ):
    ''' Initializes bootstrapping of discord.py application. '''
    self.__prefix_sanity_check(prefix)
    self.intents = intents
    self.config_file = config_file
    self.initialize_bot()

  def __prefix_sanity_check(self, prefix : PrefixType):
    if prefix is UNDEFINED:
      raise ValueError('Bot Prefix is required.')
    self.prefix = prefix

  def __token_sanity_check(self, token : str):
    if token is UNDEFINED:
      raise ValueError('Bot Token is required.')
    self.token = token

  def initialize_bot(self):
    ''' Bootstrapping bot initialization process. '''
    shared.load_config(self.config_file, config_class = self.config_class)
    self.token = shared.config.cred.token
    self.bot = commands.Bot(
      self.prefix,
      **self.parameters,
    )
    self.initialize_bot_events()

  def initialize_bot_events(self):
    ''' Bootstrapping bot events initialization process. '''
    self.bot.listen('on_c/file_change')(self.__bot_update_config)
    self.bot.event(on_command_error)

  async def __bot_update_config(self, file):
    if file != self.config_file:
      return

    log.info("Updating file configuration.")
    shared.load_config(file, config_class = self.config_class)
    self.bot.dispatch('c/config_update')

  async def bot_setup(self):
    ''' Bootstrap application connection setup. '''
    await self.bot_setup_logger()
    await self.__bot_setup_core_function()
    await self.bot_setup_additional_function()
    await self.__bot_setup_finalize()

  async def bot_setup_logger(self):
    ''' Initializes application logger. '''
    handler = logging.StreamHandler(stream=sys.stderr)
    setup_logging(handler=handler)

  async def __bot_setup_core_function(self):
    log.debug('Installing core cogs,,,')
    await self.bot.add_cog(plugins.watch.File(self.bot, [self.config_file]))
    await self.bot.add_cog(plugins.sync.Feature(self.bot))

  async def bot_setup_additional_function(self):
    ''' Performs extra initialization step. This function is for overriding. '''
    pass

  async def __bot_setup_finalize(self):
    log.debug('Logging in')
    await self.bot.start(
      self.token,
      reconnect=True,
    )

  async def bot_teardown(self):
    ''' Bootstrap application connection teardown. By default there's no teardown definition. '''
    pass


  async def sync_commands(self):
    ''' Synchronize commands for CLI use. '''

    async with self.bot:
      self.bot._connection.application_id = shared.config.cred.id
      await self.bot.http.static_login(self.token)
      await self.bot.tree.sync(guild=None)
      for serverID in self.bot.tree._guild_commands.keys():
        await self.bot.tree.sync(guild=serverID)

  async def startup(self):
    ''' Starts up the application with bootstrap flow. '''

    async with self:
      pass

  def cli_boot(self):
    ''' Execute application with predefined set of arguments. '''

    def mode_normal():
      log.info(
        'Invite: %s',
         oauth_url(
          shared.config.cred.id,
          permissions=discord.Permissions(0),
        ),
      )

      asyncio.run(self.startup())

    def mode_quick_sync():
      log.info('Syncing commands...')
      asyncio.run(self.sync_commands())

    result   = argparse.Namespace(
      callback=mode_normal,
    )
    parser   = argparse.ArgumentParser()
    parser.add_argument(
      '--sync', action='store_const', const=mode_quick_sync, dest='callback',
      help='updates bot slash command and exit',
    )
    parser.parse_args(namespace=result)
    result.callback()

  async def __aenter__(self):
    await self.bot.__aenter__()
    await self.bot_setup()
    return self.bot

  async def __aexit__(self, exc_type, exc, exc_trace):
    await self.bot_teardown()

    if exc_type is KeyboardInterrupt:
      return True
    else:
      return await self.bot.__aexit__(exc_type, exc, exc_trace)

  @property
  def parameters(self):
    return {
      'intents': self.intents,
      'help_command': None,
    }

async def on_command_error(ctx, error):
  ''' Prevents error logging for command not found. '''

  if isinstance(error, EventInterrupt):
    return

  if isinstance(error, CommandNotFound):
    return

  log.error('Exception found in command %s', ctx.command, exc_info=error)

__all__ = [
  'Application',
]
