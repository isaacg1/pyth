#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='pyth',
    version='4.4.1',
    description='Pyth, an extremely concise language',
    author='isaacg1',
    url='https://github.com/isaacg1/pyth',
    license='Expat',
    py_modules=['pyth','macros','data','big-pyth','extra_parse','lexer','packed-pyth','test','tree']
)
