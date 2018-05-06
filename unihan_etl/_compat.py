# -*- coding: utf8 -*-
# flake8: noqa

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    unichr = unichr
    text_type = unicode
    string_types = (str, unicode)

    from cStringIO import StringIO as BytesIO
    from StringIO import StringIO

    from urllib import urlretrieve
    from itertools import izip

    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')
else:
    unichr = chr
    text_type = str
    string_types = (str,)

    from io import StringIO, BytesIO

    from urllib.request import urlretrieve
    izip = zip

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise(value.with_traceback(tb))
        raise value
