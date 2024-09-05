from typing import Type

from .config import Config

config = None

def load_config(file : str, *, config_class : Type[Config]):
  '''
  Loads or updates config data.
  '''
  import yaml
  global config

  c = yaml.load(open(file).read(), Loader=yaml.Loader)
  if config is None:
    config = config_class(c)
  else:
    config.update(c)

__all__ = [
  'config', 'load_config',
]
