"""
WialonSDK example usage
"""
from wialon.sdk import SdkException, WialonError, WialonSdk

# Initialize Wialon instance
sdk = WialonSdk(
  is_development=True,
  scheme='https',
  host='hst-api.wialon.com',
  port=0,
  session_id='',
  extra_params={},
)

try:
  token = ''  # If you haven't a token, you should use our token generator
  # https://goldenmcorp.com/resources/token-generator
  response = sdk.login(token)
  print(response)

  parameters = {
    'spec': {
      'itemsType': str,
      'propName': str,
      'propValueMask': str,
      'sortType': str,
      'propType': str,
      'or_logic': bool
    },
    'force': int,
    'flags': int,
    'from': int,
    'to': int
  }

  units = sdk.core_search_items(parameters)

  sdk.logout()
except SdkException as e:
  print(f'Sdk related error: {e}')
except WialonError as e:
  print(f'Wialon related error: {e}')
except Exception as e:
  print(f'Python error: {e}')
