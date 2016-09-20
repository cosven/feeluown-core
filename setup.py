#!/usr/bin/env python3

from setuptools import setup

import fuocore


setup(
    name='fuocore',
    version=fuocore.__version__,
    description='feeluown core',
    author='Cosven',
    author_email='cosven.yin@gmail.com',
    packages=['fuocore'],
    package_data={
        '': []
        },
    url='https://github.com/cosven/feeluown-core',
    keywords=['media', 'player', 'api'],
    classifiers=(
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        ),
    install_requires=[
        'pycrypto',
        'requests',
        'beautifulsoup4',
        ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': []
        },
    )
