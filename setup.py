#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

import sentry_skype


setup(
    name='sentry_skype',
    version=sentry_skype.__version__,
    packages=['sentry_skype'],
    url='https://github.com/IvanBabushkin/sentry-skype',
    author='Ivan Babushkin',
    author_email='',
    description='Plugin for Sentry which allows sending notification via Skype.',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    include_package_data=True,
)
