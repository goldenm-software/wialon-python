"""Setup file"""
import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="wialon", # Replace with your own username
  version="1.0.3",
  author="Golden M",
  author_email="support@goldenmcorp.com",
  description="Wialon Remote API for Python",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/goldenm-software/wialon-python",
  packages=setuptools.find_packages(),
  python_requires='>=3.6',
)
