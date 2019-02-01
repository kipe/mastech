#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='mastech',
    version='0.0.1',
    description='A library for reading Mastech multimeters.',
    author='Kimmo Huoman',
    author_email='kipenroskaposti@gmail.com',
    url='https://github.com/kipe/mastech',
    license='MIT',
    packages=[
        'mastech',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'bluepy>=1.3.0',
        'pendulum>=2.0.4',
    ])
