# wialon-python
wialon-python is a Wialon Remote API Wrapper for python language.

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/goldenm-software/wialon-python/blob/master/LICENSE)
[![pypi version](https://badge.fury.io/py/wialon.svg)](https://pypi.org/project/wialon/)

## Installation

Use the package manager [pip](https://pypi.org/) to install wialon-pythonn.

```bash
pip3 install wialon
```

## Usage

```python
from wialon.sdk import WialonError, WialonSdk

is_development = True
scheme = 'https'
host = 'hst-api.wialon.com'
port = 0
session_id = ''
extra_params = {}

# Initialize Wialon instance
wialon = WialonSdk(is_development=is_development, scheme=scheme, host=host, port=port, session_id=session_id, extra_params=extra_params)

try:
  # Login with API Token
  response = wialon.login('YourTokenHere')
  print(response)
  
  # Logout
  wialon.logout()
except WialonError as e:
  # Wialon error handler
  print(e)
except Exception as e:
  print("Other errors related to code - {e}".format(e=e))

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)