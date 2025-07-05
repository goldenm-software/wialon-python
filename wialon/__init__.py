""" wialon unified namespace """
import sys

if sys.version_info >= (3, 13):
  __path__ = __import__('pkgutil').extend_path(__path__, __name__)
else:
  try:
    import pkg_resources

    pkg_resources.declare_namespace(__name__)
  except ImportError:
    import pkgutil

    __path__ = pkgutil.extend_path(__path__, __name__)  # type: ignore


from .sdk import SdkException, WialonError, WialonSdk

__all__ = ['SdkException', 'WialonError', 'WialonSdk']
