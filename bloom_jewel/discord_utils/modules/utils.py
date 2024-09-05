from inspect import iscoroutinefunction as callableasync
from . import shared

async def is_owner(ctx):
  '''
  Determine owner of the bot.
  '''
  if hasattr(shared.config, 'users'):
    return ctx.author.id in shared.config.users
  elif ctx.bot.application is not None:
    app = ctx.bot.application
    owners = frozenset(
      [app.owner.id]
      if app.team is None else
      [member.id for member in app.team.members]
    )
    return ctx.author.id in owners
  else:
    return False

async def call_function(fun, *args, **kwargs):
  '''
  Calls function with assumption of async function.
  '''
  if callableasync(fun):
    await fun(*args, **kwargs)
  elif callable(fun):
    fun(*args, **kwargs)

is_manager = is_owner
