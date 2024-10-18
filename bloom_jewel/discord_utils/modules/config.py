import abc

class Config(metaclass=abc.ABCMeta):
  '''
  Application simple config structure.
  '''

  @abc.abstractmethod
  def __init__(self, data):
    self.cred = Credential(data['bot'])
    ...

  @abc.abstractmethod
  def update(self, data):
    '''
    Update configuration data.
    '''
    self.cred.update(data['bot'])
    ...

class Credential:
  '''
  Application credential data.
  '''

  def __init__(self, data):
    self.update(data)

  def update(self, data):
    self.id = data.get('id', None)
    self.token = data['token']

__all__ = [
  'Config',
]
