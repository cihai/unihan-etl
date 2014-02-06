#!/usr/bin/env python
# -*- coding: utf8 - *-
"""Tool to build `Unihan`_ dataset into datapackage / simple data format."""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

__title__ = 'cihaidata-python'
__package_name__ = 'cihaidata_python'
__description__ = 'Tool to build `Unihan`_ dataset into datapackage / simple data format.'
__version__ = '0.0.1'
__author__ = 'Tony Narlock'
__email__ = 'cihai@git-pull.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013-2014 Tony Narlock'


from .unihan import Unihan, check_install, create_table, flatten_datasets
from .scripts import save, download, extract, convert
