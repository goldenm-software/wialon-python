"""SDK classes"""
import json
import logging

import requests

log = logging.getLogger('wialon.sdk')


class WialonSdk:
  """Sdk handler"""

  def __init__(
    self,
    is_development: bool = False,
    scheme: str = 'https',
    host: str = 'hst-api.wialon.com',
    port: int = 0,
    session_id: str = '',
    extra_params: dict = None,
  ):
    """
    Constructor
    ---
    Arguments:
      - is_development : defines if the SDK is in development mode, this argument was deprecated
                         in favor of logging module (logging.DEBUG level)
      - scheme : defines the scheme to use, default is https
      - host : defines the host to use, default is hst-api.wialon.com
      - port : defines the port to use, default is 0. If the port is different to 0, the SDK will
               use the scheme://host:port to perform any request, otherwise, the SDK will use
               https://host to perform any request
      - session_id : defines the session_id to use, default is empty string
      - extra_params : defines the extra_params to use, default is None
    """
    self._debug = is_development
    if not isinstance(scheme, str):
      raise SdkException(message='Invalid scheme, must be string')
    self._scheme = scheme

    if not isinstance(host, str):
      raise SdkException(message='Invalid host, must be string')
    self._host = host

    if not isinstance(port, int):
      raise SdkException(message='Invalid port, must be integer')
    self._port = port

    if not isinstance(session_id, str):
      raise SdkException(message='Invalid session_id, must be string')
    self._session_id = session_id

    self._default_params = {}

    if extra_params is not None:
      if not isinstance(extra_params, dict):
        raise SdkException(message='Invalid extra_params, must be dict')
      self._default_params.update(extra_params)

    self._user_id = ''

  @property
  def base_url(self) -> str:
    """ Get the base URL to perform any request """
    if self._port > 0:
      url = f'{self._scheme}://{self._host}:{self._port}'
    else:
      url = f'{self._scheme}://{self._host}'

    return f'{url}/wialon/ajax.html?'

  def call(self, method: str, args: [dict | list]) -> dict:
    """
    Call method
    Allows to call any method in the Remtoe API using the following rule:
    To get the SVC, uses the default __getattr__ method to convert the Remote API SVC to a flat
    method in Python, for example:
    core/search_items -> core_search_items

    Arguments:
      - method : defines the method to call
      - args : defines the arguments to use, must be a dict, in case if the method requires a list,
               the default_params will be ignored

    Returns:
      - dict : the response from the server

    Raises:
      - SdkException : if any error occurs
      - WialonError : if the server returns an error
    """
    svc = None

    if method == 'unit_group_update_units':
      svc = 'unit_group/update_units'
    else:
      svc = str(method).replace('_', '/', 1)

    arguments = {}
    arguments.update(self._default_params)

    if isinstance(args, list):
      arguments = args
    else:
      arguments.update(args)

    try:
      params = json.dumps(arguments)
    except Exception as e:
      raise SdkException(f'Internal error: {e}') from e

    parameters = {
      'svc': svc,
      'params': params,
      'sid': self._session_id,
    }

    url = self.base_url
    for key, value in parameters.items():
      url += f'{key}={value}&'

    log.debug(
      'Call method: %s - svc: %s - params: %s - sessionId: %s',
      method,
      svc,
      params,
      self._session_id,
    )
    log.debug('Call url: %s', url)

    try:
      request = requests.post(url=url)
    except Exception as e:
      raise SdkException(f'Internal error: {e}') from e

    try:
      response = request.json()
    except Exception as e:
      raise SdkException(f'Internal error: {e}') from e

    if 'error' in response and response['error'] != 0:
      reason = ''
      if 'reason' in response:
        reason = response['reason']

      raise WialonError(code=response['error'], reason=reason)

    return response

  def login(self, token: str):
    """Login shortcut method"""
    result = self.token_login({'token': token})

    self._user_id = result['user']['id']
    self._session_id = result['eid']

    return result

  def logout(self):
    """Logout shortcut method"""
    self.core_logout()

  def reverse_geocoding(self, latitude: float, longitude: float, flags: int = 1255211008):
    """Reverse geocoding service"""

    coordinates = json.dumps({'lon': longitude, 'lat': latitude})

    url = f'https://geocode-maps.wialon.com/{self.host}/gis_geocode?'
    url += f'coords=[{coordinates}]&flags={flags}&uid={self.user_id}'

    log.debug('Reverse geocoding called: latitude %s - longitude %s - flags %s', latitude, longitude, flags)
    log.debug('Reverse geocoding url: %s', url)

    try:
      request = requests.post(url=url)
      response = request.json()
      return response[0]
    except Exception as e:  #pylint: disable=W0706
      raise SdkException(message=f'Internal error: {e}') from e

  def __getattr__(self, name: str):
    """ Method missing handler """

    def method(*args: dict):
      """Handler"""
      arguments = {}

      if len(args) > 0:
        arguments = args[0]

      return self.call(name, arguments)

    return method


class SdkException(BaseException):
  """Sdk general exceptions"""
  _message = ''

  def __init__(self, message='Exception'):
    """Constructor"""
    self._message = message
    super().__init__()

  def _readable(self):
    """Readable property"""
    return f'SdkException(message: {self._message})'

  def __str__(self):
    """Readable property"""
    return self._readable()

  def __repr__(self):
    """Readable property"""
    return self._readable()


class WialonError(BaseException):
  """Error handler class"""

  _errors = {
    '-1': 'Unhandled error code',
    '1': 'Invalid session',
    '2': 'Invalid service name',
    '3': 'Invalid result',
    '4': 'Invalid input',
    '5': 'Error performing request',
    '6': 'Unknown error',
    '7': 'Access denied',
    '8': 'Invalid user name or password',
    '9': 'Authorization server is unavailable',
    '10': 'Reached limit of concurrent requests',
    '11': 'Password reset error',
    '14': 'Billing error',
    '1001': 'No messages for selected interval',
    '1002': 'Item with such unique property already exists or Item'\
          + 'cannot be created according to billing restrictions',
    '1003': 'Only one request is allowed at the moment',
    '1004': 'Limit of messages has been exceeded',
    '1005': 'Execution time has exceeded the limit',
    '1006': 'Exceeding the limit of attempts to enter a two-factor authorization code',
    '1011': 'Your IP has changed or session has expired',
    '2014': 'Selected user is a creator for some system objects, thus this user cannot'\
          + 'be bound to a new account',
    '2015': 'Sensor deleting is forbidden because of using in another sensor or advanced'\
          + 'properties of the unit'
  }

  _code = '0'

  _reason = ''

  def __init__(self, code, reason):
    """Constructor"""
    print('Error code: ', code)
    if str(code) not in self._errors:
      self._reason = self._errors['-1']
      self._code = '-1'
    else:
      self._reason = self._errors[str(code)]
      self._code = str(code)

    if len(reason) > 0:
      self._reason += f' - {reason}'

    super().__init__()

  def _readable(self):
    """Readable property"""
    return f'WialonError(code: {self._code}, reason: {self._reason})'

  def __str__(self):
    """Readable property"""
    return self._readable()

  def __repr__(self):
    """Readable property"""
    return self._readable()
