*unihan-etl* - `ETL`_ tool for Unicode's Han Unification (`UNIHAN`_) database
releases. unihan-etl retrieves (downloads), extracts (unzips), and transforms the
database from Unicode's website to a flat, tabular or structured, tree-like
format.

unihan-etl can be used as a python library through its `API`_, to retrieve data
as a python object, or through the `CLI`_ to retrieve a CSV, JSON, or YAML file.

Part of the `cihai`_ project. Similar project: `libUnihan <http://libunihan.sourceforge.net/>`_.

UNIHAN Version compatibility (as of unihan-etl v0.10.0):
`11.0.0 <https://www.unicode.org/reports/tr38/tr38-25.html#History>`__
(released 2018-05-08, revision 25).

|pypi| |docs| |build-status| |coverage| |license|

`UNIHAN`_'s data is dispersed across multiple files in the format of::

    U+3400	kCantonese	jau1
    U+3400	kDefinition	(same as U+4E18 丘) hillock or mound
    U+3400	kMandarin	qiū
    U+3401	kCantonese	tim2
    U+3401	kDefinition	to lick; to taste, a mat, bamboo bark
    U+3401	kHanyuPinyin	10019.020:tiàn
    U+3401	kMandarin	tiàn

Values vary in shape and structure depending on their field type.
`kHanyuPinyin <http://www.unicode.org/reports/tr38/#kHanyuPinyin>`_
maps Unicode codepoints to `Hànyǔ Dà Zìdiǎn <https://en.wikipedia.org/wiki/Hanyu_Da_Zidian>`_,
where ``10019.020:tiàn`` represents an entry. Complicating it further,
more variations::

    U+5EFE	kHanyuPinyin	10513.110,10514.010,10514.020:gǒng
    U+5364	kHanyuPinyin	10093.130:xī,lǔ 74609.020:lǔ,xī

*kHanyuPinyin* supports multiple entries delimited by spaces. ":"
(colon) separate locations in the work from pinyin readings. ","
(comma) separate multiple entries/readings. This is just one of 90 
fields contained in the database.

.. _API: https://unihan-etl.git-pull.com/en/latest/api.html
.. _CLI: https://unihan-etl.git-pull.com/en/latest/cli.html

Tabular, "Flat" output
----------------------

CSV (default), ``$ unihan-etl``::

   char,ucn,kCantonese,kDefinition,kHanyuPinyin,kMandarin
   㐀,U+3400,jau1,(same as U+4E18 丘) hillock or mound,,qiū
   㐁,U+3401,tim2,"to lick; to taste, a mat, bamboo bark",10019.020:tiàn,tiàn

With ``$ unihan-etl -F yaml --no-expand``:

.. code-block:: yaml

   - char: 㐀
     kCantonese: jau1
     kDefinition: (same as U+4E18 丘) hillock or mound
     kHanyuPinyin: null
     kMandarin: qiū
     ucn: U+3400
   - char: 㐁
     kCantonese: tim2
     kDefinition: to lick; to taste, a mat, bamboo bark
     kHanyuPinyin: 10019.020:tiàn
     kMandarin: tiàn
     ucn: U+3401

With ``$ unihan-etl -F json --no-expand``:

.. code-block:: json

   [
     {
       "char": "㐀",
       "ucn": "U+3400",
       "kDefinition": "(same as U+4E18 丘) hillock or mound",
       "kCantonese": "jau1",
       "kHanyuPinyin": null,
       "kMandarin": "qiū"
     },
     {
       "char": "㐁",
       "ucn": "U+3401",
       "kDefinition": "to lick; to taste, a mat, bamboo bark",
       "kCantonese": "tim2",
       "kHanyuPinyin": "10019.020:tiàn",
       "kMandarin": "tiàn"
     }
   ]

"Structured" output
-------------------

Codepoints can pack a lot more detail, unihan-etl carefully extracts these values
in a uniform manner. Empty values are pruned.

To make this possible, unihan-etl exports to JSON, YAML, and python
list/dicts.

.. admonition:: Why not CSV?
   
   Unfortunately, CSV is only suitable for storing table-like 
   information. File formats such as JSON and YAML accept key-values and
   hierarchical entries.

JSON, ``$ unihan-etl -F json``:

.. code-block:: json

  [
    {
      "char": "㐀",
      "ucn": "U+3400",
      "kDefinition": [
        "(same as U+4E18 丘) hillock or mound"
      ],
      "kCantonese": [
        "jau1"
      ],
      "kMandarin": {
        "zh-Hans": "qiū",
        "zh-Hant": "qiū"
      }
    },
    {
      "char": "㐁",
      "ucn": "U+3401",
      "kDefinition": [
        "to lick",
        "to taste, a mat, bamboo bark"
      ],
      "kCantonese": [
        "tim2"
      ],
      "kHanyuPinyin": [
        {
          "locations": [
            {
              "volume": 1,
              "page": 19,
              "character": 2,
              "virtual": 0
            }
          ],
          "readings": [
            "tiàn"
          ]
        }
      ],
      "kMandarin": {
        "zh-Hans": "tiàn",
        "zh-Hant": "tiàn"
      }
    }
   ]

YAML ``$ unihan-etl -F yaml``:

.. code-block:: yaml

   - char: 㐀
     kCantonese:
     - jau1
     kDefinition:
     - (same as U+4E18 丘) hillock or mound
     kMandarin:
       zh-Hans: qiū
       zh-Hant: qiū
     ucn: U+3400
   - char: 㐁
     kCantonese:
     - tim2
     kDefinition:
     - to lick
     - to taste, a mat, bamboo bark
     kHanyuPinyin:
     - locations:
       - character: 2
         page: 19
         virtual: 0
         volume: 1
       readings:
       - tiàn
     kMandarin:
       zh-Hans: tiàn
       zh-Hant: tiàn
     ucn: U+3401


Features
--------

* automatically downloads UNIHAN from the internet
* strives for accuracy with the specifications described in `UNIHAN's database
  design <http://www.unicode.org/reports/tr38/>`_
* export to JSON, CSV and YAML (requires `pyyaml`_) via ``-F``
* configurable to export specific fields via ``-f``
* accounts for encoding conflicts due to the Unicode-heavy content
* designed as a technical proof for future CJK (Chinese, Japanese,
  Korean) datasets
* core component and dependency of `cihai`_, a CJK library
* `data package`_ support
* expansion of multi-value delimited fields in YAML, JSON and python
  dictionaries 
* supports >= 3.6 and pypy

If you encounter a problem or have a question, please `create an
issue`_.

.. _cihai: https://cihai.git-pull.com
.. _cihai-handbook: https://github.com/cihai/cihai-handbook
.. _cihai team: https://github.com/cihai?tab=members
.. _cihai-python: https://github.com/cihai/cihai-python

Usage
-----

``unihan-etl`` offers customizable builds via its command line arguments.

See `unihan-etl CLI arguments`_ for information on how you can specify 
columns, files, download URL's, and output destination.

To download and build your own UNIHAN export:

.. code-block:: bash

   $ pip install --user unihan-etl

To output CSV, the default format:

.. code-block:: bash

    $ unihan-etl

To output JSON::

    $ unihan-etl -F json

To output YAML::

    $ pip install --user pyyaml
    $ unihan-etl -F yaml

To only output the kDefinition field in a csv::

    $ unihan-etl -f kDefinition

To output multiple fields, separate with spaces::

    $ unihan-etl -f kCantonese kDefinition

To output to a custom file::

    $ unihan-etl --destination ./exported.csv

To output to a custom file (templated file extension)::

    $ unihan-etl --destination ./exported.{ext}

See `unihan-etl CLI arguments`_ for advanced usage examples.

.. _unihan-etl CLI arguments: https://unihan-etl.git-pull.com/en/latest/cli.html

Code layout
-----------

.. code-block:: bash

    # cache dir (Unihan.zip is downloaded, contents extracted)
    {XDG cache dir}/unihan_etl/

    # output dir
    {XDG data dir}/unihan_etl/
      unihan.json
      unihan.csv
      unihan.yaml   # (requires pyyaml)

    # package dir
    unihan_etl/
      process.py    # argparse, download, extract, transform UNIHAN's data
      constants.py  # immutable data vars (field to filename mappings, etc)
      expansion.py  # extracting details baked inside of fields
      _compat.py    # python 2/3 compatibility module
      util.py       # utility / helper functions

    # test suite
    tests/*

Developing
----------
`poetry`_ is a required package to develop.

``git clone https://github.com/cihai/unihan-etl.git``

``cd unihan-etl``

``poetry install -E "docs test coverage lint format"``

Makefile commands prefixed with ``watch_`` will watch files and rerun.

Tests
"""""

``poetry run py.test``

Helpers: ``make test``
Rerun tests on file change: ``make watch_test`` (requires `entr(1)`_)

Documentation
"""""""""""""
Default preview server: http://localhost:8039

``cd docs/`` and ``make html`` to build. ``make serve`` to start http server.

Helpers:
``make build_docs``, ``make serve_docs``

Rebuild docs on file change: ``make watch_docs`` (requires `entr(1)`_)

Rebuild docs and run server via one terminal: ``make dev_docs``  (requires above, and a 
``make(1)`` with ``-J`` support, e.g. GNU Make)

Formatting / Linting
""""""""""""""""""""
The project uses `black`_ and `isort`_ (one after the other) and runs `flake8`_ via 
CI. See the configuration in `pyproject.toml` and `setup.cfg`:

``make black isort``: Run ``black`` first, then ``isort`` to handle import nuances
``make flake8``, to watch (requires ``entr(1)``): ``make watch_flake8`` 

Releasing
"""""""""

As of 0.11, `poetry`_ handles virtualenv creation, package requirements, versioning,
building, and publishing. Therefore there is no setup.py or requirements files.

Update `__version__` in `__about__.py` and `pyproject.toml`::

	git commit -m 'build(unihan-etl): Tag v0.1.1'
	git tag v0.1.1
	git push
	git push --tags
	poetry build
	poetry deploy

.. _UNIHAN: http://www.unicode.org/charts/unihan.html
.. _ETL: https://en.wikipedia.org/wiki/Extract,_transform,_load
.. _create an issue: https://github.com/cihai/unihan-etl/issues/new
.. _Data Package: http://frictionlessdata.io/data-packages/
.. _pyyaml: http://pyyaml.org/
.. _poetry: https://python-poetry.org/
.. _entr(1): http://eradman.com/entrproject/
.. _black: https://github.com/psf/black
.. _isort: https://pypi.org/project/isort/
.. _flake8: https://flake8.pycqa.org/

.. |pypi| image:: https://img.shields.io/pypi/v/unihan-etl.svg
    :alt: Python Package
    :target: http://badge.fury.io/py/unihan-etl

.. |docs| image:: https://github.com/cihai/unihan-etl/workflows/Publish%20Docs/badge.svg
   :alt: Docs
   :target: https://github.com/cihai/unihan-etl/actions?query=workflow%3A"Publish+Docs"

.. |build-status| image:: https://github.com/cihai/unihan-etl/workflows/tests/badge.svg
   :alt: Build Status
   :target: https://github.com/cihai/unihan-etl/actions?query=workflow%3A"tests"

.. |coverage| image:: https://codecov.io/gh/cihai/unihan-etl/branch/master/graph/badge.svg
    :alt: Code Coverage
    :target: https://codecov.io/gh/cihai/unihan-etl

.. |license| image:: https://img.shields.io/github/license/cihai/unihan-etl.svg
    :alt: License 
