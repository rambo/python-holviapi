# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='holviapi',
    version='0.1.20160112',
    author='Eero "rambo" af Heurlin',
    author_email='rambo@iki.fi',
    packages=['holviapi', 'holviapi.errors', ],
    license='MIT',
    long_description=open('README.md').read(),
    description='Implement Pythonic wrappers for Holvi JSON-REST API',
    install_requires=list(filter(bool, (x.strip() for x in open('requirements.txt').readlines()))),
    url='https://github.com/rambo/python-holviapi',
)
