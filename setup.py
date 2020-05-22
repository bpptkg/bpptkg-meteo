#!/usr/bin/env python

import os
from setuptools import setup, find_packages

from meteo import __version__


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='bpptkg-meteo',
    version=__version__,
    description='BPPTKG weather station data fetcher and schema tables library.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    install_requires=[
        'sqlalchemy',
    ],
    author='Indra Rudianto',
    author_email='indrarudianto.official@gmail.com',
    zip_safe=False,
    packages=find_packages(exclude=['docs', 'tests', 'examples']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
