import io
import os
import re

try:
    from setuptools import setup , find_packages
except ImportError:
    from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read the version from the __init__.py file without importing it
def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")
setup(
    name='DG2',
    version='0.0.1',
    packages=find_packages(),
    install_requires=requirements,
    url='www.nrel.gov/tools/DG2',
    license='BSD 3 clause',
    author='Aadil Latif',
    author_email='aadil.latif@nrel.gov',
    description='Web interface to OpenDSS for PV integration studies',
    package_data={'DG2': []},
)
