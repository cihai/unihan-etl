*unihan-etl* - `ETL`_ tool `UNIHAN`_. Retrieve, extract, and transform
the UNIHAN database into tabular or structured format. Load into python objects,
JSON, CSV, and YAML.  Part of the `cihai`_ project. See also: `libUnihan <http://libunihan.sourceforge.net/>`_.

|pypi| |docs| |build-status| |coverage| |license|

`UNIHAN`_'s data is dispersed across multiple files in the format of::

    U+3400	kCantonese	jau1
    U+3400	kDefinition	(same as U+4E18 丘) hillock or mound
    U+3400	kMandarin	qiū
    U+3401	kCantonese	tim2
    U+3401	kDefinition	to lick; to taste, a mat, bamboo bark
    U+3401	kHanyuPinyin	10019.020:tiàn
    U+3401	kMandarin	tiàn

Field types contain additional information to extract. For example,
`kHanyuPinyin <http://www.unicode.org/reports/tr38/#kHanyuPinyin>`_,
which maps Unicode codepoints to `Hànyǔ Dà Zìdiǎn <https://en.wikipedia.org/wiki/Hanyu_Da_Zidian>`_,
``10019.020:tiàn`` represents a minimal case. More::

    U+5EFE	kHanyuPinyin	10513.110,10514.010,10514.020:gǒng
    U+5364	kHanyuPinyin	10093.130:xī,lǔ 74609.020:lǔ,xī

The *kHanyuPinyin* field supports multiple entries, delimited by spaces.
Within an entry, a ":" (colon) separates locations in the work and pinyin
readings. Within these split values, a "," (comma) can separate multiple
values. This is just one of 90 fields contained in the database.

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

The UNIHAN database packs multiple values, nested values, and optional flags
(such as apostrophes) into fields. unihan-etl carefully extracts these values in
a uniform manner. Empty values are pruned.

Due to the nested nature of this output, its only supported on JSON, YAML, and
python output.

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
* supports python 2.7, >= 3.5 and pypy

If you encounter a problem or have a question, please `create an
issue`_.

.. _cihai: https://cihai.git-pull.com
.. _cihai-handbook: https://github.com/cihai/cihai-handbook
.. _cihai team: https://github.com/cihai?tab=members
.. _cihai-python: https://github.com/cihai/cihai-python

Usage
-----

``unihan-etl`` supports command line arguments. See `unihan-etl CLI
arguments`_ for information on how you can specify custom columns, files,
download URL's and output destinations.

To download and build your own UNIHAN export:

.. code-block:: bash

   $ pip install unihan-etl

To output CSV, the default format:

.. code-block:: bash

    $ unihan-etl

To output JSON::

    $ unihan-etl -F json

To output YAML::

    $ pip install pyyaml
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

Structure
---------

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

.. _UNIHAN: http://www.unicode.org/charts/unihan.html
.. _ETL: https://en.wikipedia.org/wiki/Extract,_transform,_load
.. _create an issue: https://github.com/cihai/unihan-etl/issues/new
.. _Data Package: http://frictionlessdata.io/data-packages/
.. _pyyaml: http://pyyaml.org/

.. |pypi| image:: https://img.shields.io/pypi/v/unihan-etl.svg
    :alt: Python Package
    :target: http://badge.fury.io/py/unihan-etl

.. |build-status| image:: https://img.shields.io/travis/cihai/unihan-etl.svg
   :alt: Build Status
   :target: https://travis-ci.org/cihai/unihan-etl

.. |coverage| image:: https://codecov.io/gh/cihai/unihan-etl/branch/master/graph/badge.svg
    :alt: Code Coverage
    :target: https://codecov.io/gh/cihai/unihan-etl

.. |license| image:: https://img.shields.io/github/license/cihai/unihan-etl.svg
    :alt: License 

.. |docs| image:: https://readthedocs.org/projects/unihan-etl/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/unihan-etl/
