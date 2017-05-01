# -*- coding: utf-8 -*-
"""Test helpers functions for downloading and processing Unihan data."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import sys


def add_to_path(path):
    """Adds an entry to sys.path if it's not already there.  This does
    not append it but moves it to the front so that we can be sure it
    is loaded.
    """
    if not os.path.isdir(path):
        raise RuntimeError('Tried to add nonexisting path')

    def _samefile(x, y):
        if x == y:
            return True
        try:
            return os.path.samefile(x, y)
        except (IOError, OSError, AttributeError):
            # Windows has no samefile
            return False
    sys.path[:] = [x for x in sys.path if not _samefile(path, x)]
    sys.path.insert(0, path)


def setup_path():
    script_path = os.path.join(
        os.path.dirname(__file__), os.pardir, 'scripts'
    )
    add_to_path(script_path)


def get_datapath(filename):

    return os.path.join(
        os.path.dirname(__file__), '..', 'tests', 'fixtures', filename
    )


def assert_dict_contains_subset(subset, dictionary, msg=None):
    for key, value in subset.items():
        assert key in dictionary, msg
        assert dictionary[key] == value, msg
