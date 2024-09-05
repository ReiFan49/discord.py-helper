from . import shared

def _request(verb : str, key : str, path : str, **kwargs):
  '''
  Builds request-parameter tuple.
  '''
  if hasattr(shared.config, 'servers'):
    server = next((s for s in shared.config.servers if s.name == key), None)
    if server is None:
      raise ValueError(f'Non-existent server key {key}!')

  if path[0] == '/':
    path = path[1:]

  kwargs.setdefault('headers', {})
  kwargs.setdefault('cookies', {})
  if verb == 'HEAD':
    kwargs.setdefault('allow_redirects', False)

  if hasattr(shared.config, 'servers'):
    kwargs['headers'].update(server.headers)
    kwargs['cookies'].update(server.cookies)
    url = server.url + path
  else:
    url = key + '/' + url

  return verb, url, kwargs

def request(verb : str, key : str, path : str, **kwargs):
  '''
  Synchronous Request wrapper through requests module.
  '''
  import requests
  verb, url, kwargs = _request(verb, key, path, **kwargs)
  return requests.request(verb, url, **kwargs)

async def arequest(verb : str, key : str, path : str, **kwargs):
  '''
  Asynchronous Request wrapper through httpx module.
  '''
  import httpx as arequests
  verb, url, kwargs = _request(verb, key, path, **kwargs)
  kwargs.setdefault('follow_redirects', kwargs.get('allow_redirects', False))
  cookies = kwargs.pop('cookies')
  kwargs.setdefault('timeout', (5.0, 90.0))
  timeout = kwargs.pop('timeout')
  async with arequests.AsyncClient(cookies=cookies, timeout=timeout) as client:
    return await client.request(verb, url, **kwargs)
