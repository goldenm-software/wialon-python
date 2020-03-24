"""SDK classes"""
import json
import requests

class WialonSdk:
  """Sdk handler"""

  def __init__(self, is_development=False, scheme='https', host='hst-api.wialon.com', port=0, session_id='', extra_params={}): #pylint: disable=dangerous-default-value,line-too-long
    """Method missing handler"""
    self.is_development = is_development
    self.session_id = session_id
    self.scheme = scheme
    self.default_params = {}
    self.default_params.update(extra_params)
    self.host = host

    parsed_port = ""

    if int(port) > 0:
      parsed_port = ":{port}".format(port=str(port))

    self.base_api_url = "{scheme}://{host}{port}/wialon/ajax.html?".format(
      scheme=self.scheme,
      host=self.host,
      port=parsed_port
    )
    self.user_id = ''

  def call(self, method, args):
    """Call method"""
    url = self.base_api_url

    svc = None

    if method == 'unit_group_update_units':
      svc = 'unit_group/update_units'
    else:
      svc = str(method).replace("_", "/", 1)

    arguments = {}
    arguments.update(self.default_params)
    if isinstance(args, list):
      arguments = args
    else:
      arguments.update(args)

    parameters = {
      'svc': svc,
      'params': json.dumps(arguments),
      'sid': self.session_id
    }

    if self.is_development:
      print("=" * 30)
      print("Query url: {url} - Params: {params}".format(url=url, params=parameters))
      print("-" * 30)
      print("{url}&svc={svc}&params={params}&sid={sid}".format(
        url=url,
        svc=parameters['svc'],
        params=parameters['params'],
        sid=parameters['sid']
      ))
      print("=" * 30)

    request = requests.post(url=url, params=parameters)
    response = request.json()

    if 'error' in response and response['error'] != 0:
      raise WialonError(response['error'])

    return response

  def login(self, token):
    """Login shortcut method"""
    try:
      result = self.token_login({'token': token})

      self.user_id = result['user']['id']
      self.session_id = result['eid']

      return result

    except WialonError as e:
      raise e
    except Exception as e: #pylint: disable=try-except-raise
      raise

  def logout(self):
    """Logout shortcut method"""
    try:
      result = self.core_logout()

      if result['error'] == 0:
        return True

      return False

    except WialonError as e:
      raise e
    except Exception as e: #pylint: disable=try-except-raise
      raise

  def reverse_geocoding(self, latitude, longitude, flags=1255211008):
    """Reverse geocoding service"""
    url = "https://geocode-maps.wialon.com/{host}/gis_geocode?coords=[{coordinates}]&flags={flags}&uid={user_id}".format(
      host=self.host,
      coordinates=json.dumps({
        'lon': longitude,
        'lat': latitude
      }),
      flags=flags,
      user_id=self.user_id
    )

    if self.is_development:
      print("=" * 30)
      print("URL: {url}".format(url=url))
      print("=" * 30)

    try:
      request = requests.post(url=url)
      response = request.json()

      return response[0]
    except Exception as _: #pylint: disable=try-except-raise
      raise

  def __getattr__(self, name):
    """Method missing handler"""

    def method(*args):
      """Handler"""
      if self.is_development:
        print("=" * 30)
        print("Query method: {name}".format(name=name))
        print("=" * 30)

        print("Arguments", len(args))

      arguments = {}

      if len(args) > 0:
        arguments = args[0]

      return self.call(name, arguments)

    return method

class WialonError(Exception):
  """Error handler class"""

  _errors = {
    '1': "Invalid session",
    '2': "Invalid service name",
    '3': "Invalid result",
    '4': "Invalid input",
    '5': "Error performing request",
    '6': "Unknown error",
    '7': "Access denied",
    '8': "Invalid user name or password",
    '9': "Authorization server is unavailable",
    '10': "Reached limit of concurrent requests",
    '11': "Password reset error",
    '14': "Billing error",
    '1001': "No messages for selected interval",
    '1002': "Item with such unique property already exists or Item cannot be created according to billing restrictions",
    '1003': "Only one request is allowed at the moment",
    '1004': "Limit of messages has been exceeded",
    '1005': "Execution time has exceeded the limit",
    '1006': "Exceeding the limit of attempts to enter a two-factor authorization code",
    '1011': "Your IP has changed or session has expired",
    '2014': "Selected user is a creator for some system objects, thus this user cannot be bound to a new account",
    '2015': "Sensor deleting is forbidden because of using in another sensor or advanced properties of the unit"
  }

  def __init__(self, code):
    """Constructor"""
    self._code = code

  def _readable(self):
    """Readable property"""
    return "WialonError(code: {code} - {message})".format(
      code=self._code,
      message=self._errors[str(self._code)]
    )

  def __str__(self):
    """Readable property"""
    return self._readable()

  def __repr__(self):
    """Readable property"""
    return self._readable()
