# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import subprocess

import six

git_version = 'UNKNOWN'
try:
    if six.PY2:
        git_version = str(subprocess.check_output(['git', 'rev-parse', '--verify', '--short', 'HEAD'])).strip()
    if six.PY3:
        git_version = subprocess.check_output(['git', 'rev-parse', '--verify', '--short', 'HEAD']).strip().decode('ascii')
except subprocess.CalledProcessError:
    pass

setup(
    name='holviapi',
    #version='0.5.1dev-%s' % git_version,
    version='0.4.20181219',
    author='Eero "rambo" af Heurlin',
    author_email='rambo@iki.fi',
    packages=['holviapi', 'holviapi.errors', ],
    license='MIT',
    long_description=open('README.md').read(),
    description='Implement Pythonic wrappers for Holvi JSON-REST API',
    install_requires=list(filter(bool, (x.strip() for x in open('requirements.txt').readlines()))),
    url='https://github.com/rambo/python-holviapi',
)
