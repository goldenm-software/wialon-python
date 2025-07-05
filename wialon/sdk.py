"""SDK classes"""

import json
import logging
import sys
from typing import Any, cast

import requests

from wialon.exceptions import SdkException, WialonError

if sys.version_info >= (3, 9):
  from collections.abc import Callable
else:
  from typing import Callable

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

log = logging.getLogger('wialon.sdk')


class WialonSdk:
  """Sdk handler"""

  _scheme: str
  _host: str
  _port: int
  _session_id: str
  _default_params: dict[str, Any]
  _user_id: str

  def __init__(
    self: Self,
    scheme: str = 'https',
    host: str = 'hst-api.wialon.com',
    port: int = 0,
    session_id: str = '',
    extra_params: dict[str, Any] | None = None,
  ) -> None:
    """
    Wialon SDK
    :param scheme: defines the scheme to use, default is https
    :type scheme: str
    :param host: defines the host to use, default is hst-api.wialon
    :type host: str
    :param port: defines the port to use, default is 0. If the port
                 is different to 0, the SDK will use the scheme://host:port to perform any request,
                 otherwise, the SDK will use https://host to perform any request
    :type port: int
    :param session_id: defines the session_id to use, default is empty string
    :type session_id: str
    :param extra_params: defines the extra_params to use, default is None
    :type extra_params: dict[str, Any] | None
    """

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
  def base_url(self: Self) -> str:
    """Get the base URL to perform any request"""
    if self._port > 0:
      url = f'{self._scheme}://{self._host}:{self._port}'
    else:
      url = f'{self._scheme}://{self._host}'

    return f'{url}/wialon/ajax.html?'

  def call(self: Self, method: str, args: dict[str, Any] | list[Any]) -> dict[str, Any] | list[Any]:
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

    parameters = {
      'svc': svc,
      'sid': self._session_id,
    }

    if isinstance(args, list):
      try:
        parameters['params'] = json.dumps(args)
      except Exception as e:
        raise SdkException(f'Internal error: {e}') from e
    else:
      try:
        arguments: dict[str, Any] = {}
        arguments.update(self._default_params)
        arguments.update(args)
        parameters['params'] = json.dumps(arguments)
      except Exception as e:
        raise SdkException(f'Internal error: {e}') from e

    url = self.base_url
    for key, value in parameters.items():
      url += f'{key}={value}&'

    log.debug(
      'Call method: %s - svc: %s - params: %s - sessionId: %s',
      method,
      svc,
      parameters.get('params', ''),
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

    return cast(dict[str, Any], response)

  def login(self: Self, token: str) -> dict[str, Any]:
    """
    Perform a login operation using a token. To get a token, you can use our own token generator tool, free to use:
    https://developers.layrz.com/tools/wialon-token-generator
    :param token: defines the token to use, must be a string

    :type token: str

    :return: the response from the server, must be a dict
    :rtype: dict[str, Any]
    """
    result = cast(dict[str, Any], self.token_login({'token': token}))

    self._user_id = result['user']['id']
    self._session_id = result['eid']

    return result

  def logout(self: Self) -> dict[str, Any]:
    """
    Logout the Wialon session. This method will invalidate the current session and clear the `session_id` and
    `user_id` properties to ensure that the session is no longer valid.

    :return: the response from the server, must be a dict
    :rtype: dict[str, Any]
    """
    return cast(dict[str, Any], self.core_logout())

  def reverse_geocoding(self: Self, latitude: float, longitude: float, flags: int = 1255211008) -> str:
    """
    Reverse geocoding method using the Wialon API.

    !Note: Your Wialon session will use the default geocoding service, that may be Google services or Wialon services.

    :param latitude: Latitude of the location to reverse geocode
    :type latitude: float
    :param longitude: Longitude of the location to reverse geocode
    :type longitude: float
    :param flags: Flags for the reverse geocoding request, default is 125521
    :type flags: int
    """

    coordinates = json.dumps({'lon': longitude, 'lat': latitude})

    url = f'https://geocode-maps.wialon.com/{self.host}/gis_geocode?'
    url += f'coords=[{coordinates}]&flags={flags}&uid={self.user_id}'

    log.debug('Reverse geocoding called: latitude %s - longitude %s - flags %s', latitude, longitude, flags)
    log.debug('Reverse geocoding url: %s', url)

    try:
      request = requests.post(url=url)
      response = request.json()
      return cast(str, response[0])
    except Exception as e:  # pylint: disable=W0706
      raise SdkException(message=f'Internal error: {e}') from e

  def __getattr__(self: Self, name: str) -> Callable[..., dict[str, Any] | list[Any]]:
    """Method missing handler"""

    def method(*args: dict[str, Any], **kwargs: dict[str, Any]) -> dict[str, Any] | list[Any]:
      """Handler"""
      arguments: dict[str, Any] = {}

      if len(args) > 0:
        arguments = args[0]

      if len(kwargs) > 0:
        arguments.update(kwargs)

      return self.call(name, arguments)

    return method


__all__ = ['WialonSdk', 'SdkException', 'WialonError']
