#!/usr/bin/env python
# -*- coding: utf8 - *-
"""cihaidata-unihan lives at <https://github.com/cihai/cihaidata-unihan>."""
import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, os.getcwd())  # we want to grab this:
from package_metadata import p

with open('requirements/base.txt') as f:
    install_reqs = [line for line in f.read().split('\n') if line]
    tests_reqs = []

if sys.version_info < (2, 7):
    install_reqs += ['argparse']
    tests_reqs += ['unittest2']

readme = open('README.rst').read()
history = open('CHANGES').read().replace('.. :changelog:', '')

setup(
    name=p.title,
    version=p.version,
    url='https://github.com/cihai/cihaidata-unihan',
    download_url='https://pypi.python.org/pypi/cihaidata-unihan',
    license=p.license,
    author=p.author,
    author_email=p.email,
    description=p.description,
    long_description=readme,
    include_package_data=True,
    install_requires=install_reqs,
    tests_require=tests_reqs,
    test_suite='testsuite',
    zip_safe=False,
    keywords=p.title,
    packages=find_packages(exclude=["doc"]),
    package_data={
        'cihaidata-unihan': ['data/*']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: MIT License",
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        "Topic :: Utilities",
        "Topic :: System :: Shells",
    ],
)
