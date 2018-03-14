#!/usr/bin/env python3

from setuptools import setup


requires = [
    'pycrypto>=2.6.1',
    'requests',
    'beautifulsoup4>=4.5.3',
    'marshmallow>=2.13.5',
    'april==2.0.0',
    'mutagen>=1.37',
    'fuzzywuzzy',
    'future',
    'enum34',
]


setup(
    name='fuocore',
    version='1.1.0',
    description='feeluown core',
    author='Cosven',
    author_email='cosven.yin@gmail.com',
    py_modules=['mpv'],
    packages=[
        'fuocore',
        'fuocore.local',
        'fuocore.netease',
        'fuocore.core',
        'fuocore.daemon',
        'fuocore.protocol',
        'fuocore.protocol.handlers',
        ],
    package_data={
        '': []
        },
    url='https://github.com/cosven/feeluown-core',
    keywords=['media', 'player', 'api'],
    classifiers=(
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        ),
    install_requires=requires,
    setup_requires=['pytest-runner'],
    test_suite="tests",
    tests_require=[
        'pytest',
        'mock',
    ],
    entry_points={
        'console_scripts': [
            'fuo = fuocore.daemon.main:main',
        ],
        'fuo.provider': [
            'local = fuocore.local.provider:LocalProvider',
            'netease = fuocore.netease.provider:NeteaseProvider',
        ],
    },
)
