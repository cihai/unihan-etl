.. image:: https://travis-ci.org/cihai/cihaidata-unihan.png?branch=master
    :target: https://travis-ci.org/cihai/cihaidata-unihan

.. image:: https://badge.fury.io/py/cihaidata-unihan.png
    :target: http://badge.fury.io/py/cihaidata-unihan

.. image:: https://coveralls.io/repos/cihai/cihaidata-unihan/badge.png?branch=master
    :target: https://coveralls.io/r/cihai/cihaidata-unihan?branch=master

``cihaidata-unihan`` - build simple data format CSV's for `unihan`_.
Provides optional integration with `cihai`_ python API.

**This project has been split into the https://github.com/cihai group.**

**This project is being split:**

``Cihai`` is a team, effort, united effort for incubating open,
permissive, high quality CJK datasets and clients.

- `cihai-handbook`_ provides documentational overviews of the history of
  CJK, the dataset standards and available client libraries.
- Official client libraries. `cihaidata-unihan`_ will be a python client for
  cihai+datapackages datasets (cjklib style).
- Public datasets maintained by `cihai team`_. Unihan will be a first
  example. See `cihaidata-unihan`_.

.. _cihai-handbook: https://github.com/cihai/cihai-handbook
.. _cihai team: https://github.com/cihai?tab=members
.. _cihaidata-unihan: https://github.com/cihai/cihaidata-unihan
.. _cihaidata-unihan: https://github.com/cihai/cihaidata-unihan

Being built against unit tests. See the `Travis Builds`_ and
`Revision History`_.

See `Internals`_ for design philosophy.

Future results
--------------

- Future versions will allow deeper introspection into results:

  - Multiple characters words
  - Phrases
  - Mispellings / similar shapes
  - Sorting results by usage, stroke
  - Breaking strings of characters into words
  - More datasets

Structure
---------

.. code-block:: bash

    # dataset metadata, schema information.
    datapackage.json

    # (future) when this package is stable, unihan.csv will be provided
    data/unihan.csv

    # script to download dataset and convert to clean CSV.
    scripts/process.py

    # cihai's python related modules, public-facing python API.
    __init__.py

    # unihan module code
    unihan.py


Cihai is *not* required for:

- ``data/unihan.csv`` - `simple data format`_ compatible csv file.
- ``scripts/process.py`` - create a ``data/unihan.csv``.

When this module is stable, ``data/unihan.csv`` will have prepared
releases, without requires using ``scripts/process.py``. ``process.py``
will not require external libraries.

Intended usage
--------------

(Not ready)

.. code-block:: bash

    $ ./scripts/process.py

Creates ``data/unihan.csv``.

Examples
--------

- https://github.com/datasets/gdp
- https://github.com/datasets/country-codes

Related links:

- CSV *Simple Data Format* (SDF): http://data.okfn.org/standards/simple-data-format
- Tools: http://data.okfn.org/tools


.. _Travis Builds: https://travis-ci.org/cihai/cihaidata-unihan/builds
.. _Revision History: https://github.com/cihai/cihaidata-unihan/commits/master
.. _cjklib: http://cjklib.org/0.3/
.. _current datasets: http://cihai.readthedocs.org/en/latest/api.html#datasets
.. _Extending: http://cihai.readthedocs.org/en/latest/extending.html
.. _permissively licensing your dataset: http://cihai.readthedocs.org/en/latest/information_liberation.html
.. _Internals: http://cihai.readthedocs.org/en/latest/internals.html

==============  ==========================================================
Python support  Python 2.7, >= 3.3
Source          https://github.com/cihai/cihaidata-unihan
Docs            http://cihai.rtfd.org
Changelog       http://cihai.readthedocs.org/en/latest/history.html
API             http://cihai.readthedocs.org/en/latest/api.html
Issues          https://github.com/cihai/cihaidata-unihan/issues
Travis          http://travis-ci.org/cihai/cihaidata-unihan
Test coverage   https://coveralls.io/r/cihai/cihaidata-unihan
pypi            https://pypi.python.org/pypi/cihai
Ohloh           https://www.ohloh.net/p/cihai
License         `BSD`_.
git repo        .. code-block:: bash

                    $ git clone https://github.com/cihai/cihaidata-unihan.git
install dev     .. code-block:: bash

                    $ git clone https://github.com/cihai/cihaidata-unihan.git cihai
                    $ cd ./cihai
                    $ virtualenv .env
                    $ source .env/bin/activate
                    $ pip install -e .
tests           .. code-block:: bash

                    $ python setup.py test
==============  ==========================================================

.. _BSD: http://opensource.org/licenses/BSD-3-Clause
.. _Documentation: http://cihai.readthedocs.org/en/latest/
.. _API: http://cihai.readthedocs.org/en/latest/api.html
.. _Unihan: http://www.unicode.org/charts/unihan.html
.. _datapackages: http://dataprotocols.org/data-packages/
.. _datapackage.json format: https://github.com/datasets/gdp/blob/master/datapackage.json
.. _json table schema: http://dataprotocols.org/json-table-schema/
.. _simple data format: http://data.okfn.org/standards/simple-data-format
.. _cihai dataset API: http://cihai.readthedocs.org/en/latest/extending.html
.. _PEP 301\: python package format: http://www.python.org/dev/peps/pep-0301/
