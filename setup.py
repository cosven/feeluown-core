#!/usr/bin/env python3

from setuptools import setup


requires = [
    'pycrypto>=2.6.1',
    'requests',
    'beautifulsoup4>=4.5.3',
    'marshmallow>=2.13.5',
    'mutagen>=1.37',
    'fuzzywuzzy',
]


setup(
    name='fuocore',
    version='2.0.1',
    description='feeluown core',
    author='Cosven',
    author_email='yinshaowen241@gmail.com',
    py_modules=['mpv'],
    packages=[
        'fuocore',
        'fuocore.local',
        'fuocore.netease',
        'fuocore.qqmusic',
        'fuocore.protocol',
        'fuocore.protocol.handlers',
        ],
    package_data={
        '': []
        },
    url='https://github.com/cosven/feeluown-core',
    keywords=['media', 'player', 'api'],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
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
            'feeluown_core_test = fuocore.main:main',
        ],
    },
)
