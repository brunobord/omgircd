"""
Packaging for omgircd3.
"""
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import omgircd3


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='omgircd3',
    version=omgircd3.__version__,
    description='A Python3 IRC server/daemon',
    long_description=long_description,
    url='https://github.com/brunobord/omgircd3',
    author='Bruno Bord',
    author_email='bruno@jehaisleprintemps.net',
    license='ISC',
    classifiers=[
        # State
        'Development Status :: 3 - Alpha',
        # OS
        'Operating System :: OS Independent',
        # Topic
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        # License
        'License :: OSI Approved :: ISC License (ISCL)',
        # Languages
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    python_requires='~=3.6',
    entry_points={
        'console_scripts': [
            'omgircd3=omgircd3.ircd:run',
        ],
    }
)
