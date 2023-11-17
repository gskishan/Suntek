from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in suntek_app/__init__.py
from suntek_app import __version__ as version

setup(
	name="suntek_app",
	version=version,
	description="custom_app",
	author="kishan",
	author_email="gskishan",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
