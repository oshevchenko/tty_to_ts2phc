# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tty2sock',
    version='0.1.0',
    description='Forward data from the serial interface to TCP socket.',
    long_description=readme,
    author='Oleksandr Shevchenko',
    author_email='shevchenko.adb@gmail.com',
    url='https://github.com/oshevchenko/tty_to_ts2phc',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
