from setuptools import setup, find_packages
from rdc.etl import __version__

# Human version
version = '.'.join(map(str, __version__))

# Read README file
with open('README.rst') as readme:
    long_description = readme.read()

# Parse classifiers
with open('classifiers.txt') as f:
    classifiers = filter(None, map(lambda s: s.strip(), f.read().split('\n')))

# Parse requirements
with open('requirements.txt') as f:
    install_requires = []
    for requirement in map(lambda s: s.strip(), f.read().split('\n')):
        _pound_pos = requirement.find('#')
        if _pound_pos != -1:
            requirement = requirement[0:_pound_pos].strip()
        if len(requirement):
            install_requires.append(requirement)

with open("README.rst") as readme:
    long_description = readme.read()

setup(name='rdc.etl',
      version=version,
      description="Extract Transform Load (ETL) toolkit for python",
      long_description=long_description,
      classifiers=classifiers,
      keywords='ETL Data-Integration',
      author='Romain Dorgueil',
      author_email='romain@dorgueil.net',
      url='http://etl.rdc.li/',
      download_url='https://github.com/rdcli/rdc.etl/tarball/' + version,
      license='Apache License, Version 2.0',
      packages=find_packages(exclude=['ez_setup', 'example', 'test']),
      include_package_data=True,
      install_requires=install_requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
