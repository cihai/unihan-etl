#!/usr/bin/env python
# -*- coding: utf8 - *-
"""cihaidata-unihan lives at <https://github.com/cihai/cihaidata-unihan>."""
import os
import sys
from setuptools import setup, find_packages


with open('requirements.pip') as f:
    install_reqs = [line for line in f.read().split('\n') if line]
    tests_reqs = []

if sys.version_info < (2, 7):
    install_reqs += ['argparse']
    tests_reqs += ['unittest2']

import re
VERSIONFILE = "__init__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    __version__ = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name='cihaidata-unihan',
    version=__version__,
    url='https://github.com/cihai/cihaidata-unihan',
    download_url='https://pypi.python.org/pypi/cihaidata-unihan',
    license='MIT',
    author='Tony Narlock',
    author_email='tony@git-pull.com',
    description='Unihan dataset for cihai and datapackages.',
    long_description=open('README.rst').read(),
    include_package_data=True,
    install_requires=install_reqs,
    tests_require=tests_reqs,
    test_suite='testsuite',
    zip_safe=False,
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
