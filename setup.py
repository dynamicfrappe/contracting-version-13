from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in contracting_13/__init__.py
from contracting_13 import __version__ as version

setup(
	name="contracting_13",
	version=version,
	description="dynamic",
	author="dynamic",
	author_email="beshoy.atef@dynamiceg.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
