import sys
import asyncio
import logging

log = logging.getLogger(__name__)

def report_on_fail(task):
  '''
  Reports on task failure.
  '''
  try:
    task.result()
  except asyncio.CancelledError:
    pass
  except Exception as e:
    log.error('%s occured on %s', str(e), task.get_name(), exc_info=True)

def exit_on_fail(task):
  '''
  Aborts on task failure.
  '''
  try:
    task.result()
  except asyncio.CancelledError:
    pass
  except Exception as e:
    log.error('%s occured on %s', str(e), task.get_name(), exc_info=True)
    sys.exit(1)

__all__ = [
  'report_on_fail',
  'exit_on_fail',
]
