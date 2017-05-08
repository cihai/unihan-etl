#!/usr/bin/env python
# -*- coding: utf8 - *-
"""Tool to build `Unihan`_ dataset into datapackage / simple data format."""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

from .unihan import Unihan, check_install, create_table, flatten_datasets
from .cihaidata_unihan import save, download, extract, convert
