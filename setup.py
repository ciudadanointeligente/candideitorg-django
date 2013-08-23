#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='candideitorg-django',
    version='0.0.1',
    description='',
    license='GNU Affero General Public License v3',
    author='Fundación Ciudadano Inteligente',
    author_email='lab@ciudadanointeligente.org',
    url='https://github.com/ciudadanointeligente/candideitorg-django',
    long_description=open('README.md', 'r').read(),

    # Not convinced that this is correct - it skips the fixture which are .js files
    packages=find_packages(),

    requires=[],
    install_requires=required,
    tests_require=[],
    classifiers=[
        # choose from https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
