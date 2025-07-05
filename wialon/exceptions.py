import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class SdkException(BaseException):
  """Sdk general exceptions"""

  _message = ''

  def __init__(self: Self, message: str = 'Exception') -> None:
    """Constructor"""
    self._message = message
    super().__init__()

  def __str__(self: Self) -> str:
    """Readable property"""
    return self._message

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'SdkException(message: {self._message})'


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
    '1002': 'Item with such unique property already exists or Item'
    + 'cannot be created according to billing restrictions',
    '1003': 'Only one request is allowed at the moment',
    '1004': 'Limit of messages has been exceeded',
    '1005': 'Execution time has exceeded the limit',
    '1006': 'Exceeding the limit of attempts to enter a two-factor authorization code',
    '1011': 'Your IP has changed or session has expired',
    '2014': 'Selected user is a creator for some system objects, thus this user cannot' + 'be bound to a new account',
    '2015': 'Sensor deleting is forbidden because of using in another sensor or advanced' + 'properties of the unit',
  }

  _code = '0'

  _reason = ''

  def __init__(self: Self, code: str, reason: str = '') -> None:
    """Constructor"""
    if str(code) not in self._errors:
      self._reason = self._errors['-1']
      self._code = '-1'
    else:
      self._reason = self._errors[str(code)]
      self._code = str(code)

    if len(reason) > 0:
      self._reason += f' - {reason}'

    super().__init__()

  def __str__(self: Self) -> str:
    """Readable property"""
    return f'{self._code} - {self._reason}'

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'WialonError(code: {self._code}, reason: {self._reason})'
