from discord.errors import DiscordException

class EventInterrupt(DiscordException):
  '''
  Exception that is used to halt current event processing.
  '''

  pass
