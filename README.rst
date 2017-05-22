*unihan-tabular* - tool to build `UNIHAN`_ into tabular-friendly formats
like python, JSON, CSV and YAML. Part of the `cihai`_ project.

|pypi| |docs| |build-status| |coverage| |license|

`UNIHAN`_'s data is dispersed across multiple files in the format of::

    U+3400	kCantonese	jau1
    U+3400	kDefinition	(same as U+4E18 丘) hillock or mound
    U+3400	kMandarin	qiū
    U+3401	kCantonese	tim2
    U+3401	kDefinition	to lick; to taste, a mat, bamboo bark
    U+3401	kHanyuPinyin	10019.020:tiàn
    U+3401	kMandarin	tiàn

``$ unihan-tabular`` will download Unihan.zip and build all files into a
single tabular friendly format.

CSV (default), ``$ unihan-tabular``::

   char,ucn,kCantonese,kDefinition,kHanyuPinyin,kMandarin
   㐀,U+3400,jau1,(same as U+4E18 丘) hillock or mound,,qiū
   㐁,U+3401,tim2,"to lick; to taste, a mat, bamboo bark",10019.020:tiàn,tiàn

JSON, ``$ unihan-tabular -F json``:

.. code-block:: json

   [
     {
       "char": "㐀",
       "ucn": "U+3400",
       "kCantonese": "jau1",
       "kDefinition": "(same as U+4E18 丘) hillock or mound",
       "kHanyuPinyin": null,
       "kMandarin": "qiū"
     },
     {
       "char": "㐁",
       "ucn": "U+3401",
       "kCantonese": "tim2",
       "kDefinition": [
         "to lick",
         "to taste, a mat, bamboo bark"
       ],
       "kHanyuPinyin": "10019.020:tiàn",
       "kMandarin": "tiàn"
     }
   ]

YAML ``$ unihan-tabular -F yaml``:

.. code-block:: yaml

    - char: 㐀
      kCantonese: jau1
      kDefinition: (same as U+4E18 丘) hillock or mound
      kHanyuPinyin: null
      kMandarin: qiū
      ucn: U+3400
    - char: 㐁
      kCantonese: tim2
      kDefinition:
      - to lick
      - to taste, a mat, bamboo bark
      kHanyuPinyin: 10019.020:tiàn
      kMandarin: tiàn
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
.. _unihan-tabular on github: https://github.com/cihai/unihan-tabular

Usage
-----

``unihan-tabular`` supports command line arguments. See `unihan-tabular CLI
arguments`_ for information on how you can specify custom columns, files,
download URL's and output destinations.

To download and build your own UNIHAN export:

.. code-block:: bash

   $ pip install unihan-tabular

To output CSV, the default format:

.. code-block:: bash

    $ unihan-tabular

To output JSON::

    $ unihan-tabular -F json

To output YAML::

    $ pip install pyyaml
    $ unihan-tabular -F yaml

To only output the kDefinition field in a csv::

    $ unihan-tabular -f kDefinition

To output multiple fields, separate with spaces::

    $ unihan-tabular -f kCantonese kDefinition

To output to a custom file::

    $ unihan-tabular --destination ./exported.csv

To output to a custom file (templated file extension)::

    $ unihan-tabular --destination ./exported.{ext}

See `unihan-tabular CLI arguments`_ for advanced usage examples.

.. _unihan-tabular CLI arguments: http://unihan-tabular.readthedocs.org/en/latest/cli.html

About
-----

The *Unicode Consortium*, authors of the `Unicode Standard`_, a way of
consistently representing and encoding the world's writing systems.

UNIHAN, short for `Han unification`_, is the effort to map CJK languages
into unified characters. A very time-consuming and painstaking challenge.

The advantage that UNIHAN provides to east asian researchers, including
sinologists and japanologists, linguists, anaylsts, language learners, and
hobbyists cannot be understated. Despite its use under the hood in many
applications and websites, it is underrepresented and often overlooked as a
source of reliable information. It's potential uses are not readily
understood without reading into the standard and wrangling the data.

It isn't readily accessible in data form for developers.
Even some of the public implementers of UNIHAN haven't fully exploited its
potential.

.. _Unicode Standard: https://en.wikipedia.org/wiki/Unicode
.. _Han unification: https://en.wikipedia.org/wiki/Han_unification

The problem
"""""""""""

It's difficult to readily take advantage of UNIHAN from raw data alone.

UNIHAN comprises over 20 MB of character information, separated
across multiple files. Within these files is *90* fields, spanning 8
general categories of data. Within some of fields, there are specific
considerations to take account of to use the data correctly, for instance:

UNIHAN's values place references to its own codepoints, such as
*kDefinition*::

    U+3400       kDefinition     (same as U+4E18 丘) hillock or mound

Another, values are delimited in various ways, for instance, by rules,
like *kDefinition*, "Major definitions are separated by semicolons, and minor
definitions by commas."::

    U+3402       kDefinition     (J) non-standard form of U+559C 喜, to like, love, enjoy; a joyful thing

More complicated yet, *kHanyuPinyin*: "multiple locations for a given
pīnyīn reading are separated by “,” (comma). The list of locations is
followed by “:” (colon), followed by a comma-separated list of one or more
pīnyīn readings. Where multiple pīnyīn readings are associated with a
given mapping, these are ordered as in HDZ (for the most part reflecting
relative commonality). The following are representative records."::

    U+3FCE  kHanyuPinyin    42699.050:fèn,fén
    U+34D8  kHanyuPinyin    10278.080,10278.090:sù
    U+5364  kHanyuPinyin    10093.130:xī,lǔ 74609.020:lǔ,xī
    U+5EFE  kHanyuPinyin    10513.110,10514.010,10514.020:gǒng

And also by spaces, such as in *kCantonese*::

    U+342B       kCantonese      gun3 hung1 zung1

And by spaces which specify different sources, like *kMandarin*, "When
there are two values, then the first is preferred for zh-Hans (CN) and the
second is preferred for zh-Hant (TW). When there is only one value, it is
appropriate for both."::

    U+7E43        kMandarin       běng bēng

So, data could be exported to a CSV, which unihan-tabular currently does,
but users would have to still be left to their own devices handle delimited
values.

The solution to allow the data to be accessible requires a format that
supports lists, hashes and hierarchies. Namely, JSON and YAML.

This in itself is inherent with pitfalls, since unihan-tabular is in python,
there are issues of encoding working as expected across versions. unihan-tabular
is tested in `continuous integration`_ against both 2.7 and python 3 to assure
consistent output.

Future versions of unihan-tabular will split the delimiters of
UNIHAN's "multi value" fields for users. This can be done in such a way there
isn't too much specialization added.

Taken further, there's the problem of how to make the data available
relationally. This is trickier because the approach to designing the
schema is opinionated: should all UNIHAN values just be dropped into a
database via UCN, Property and value and we create an ORM mapping for it?
Or should be keep single value properties in columns, and multi-value
properties be separated by `associative tables`_.

What needs to be done to make the data open as possible? Would a sqlite
database dump be the best way to help? A SQLAlchemy ORM class for accessing the
data? These are the areas this unihan-tabular aims to help with.

Overcoming the above challenges in harnessing the UNIHAN's data to furnish
exports in various degrees of normalization (tabularized, hierarchical, and
relation) will be of great advantage to stakeholders in east asian studies
and languages.

.. _associative tables: https://en.wikipedia.org/wiki/Associative_entity
.. _continuous integration: https://travis-ci.org/cihai/unihan-tabular

Structure
---------

.. code-block:: bash

    # output w/ JSON
    {XDG data dir}/unihan_tabular/unihan.json

    # output w/ CSV
    {XDG data dir}/unihan_tabular/unihan.csv

    # output w/ yaml (requires pyyaml)
    {XDG data dir}/unihan_tabular/unihan.yaml

    # script to download + build a SDF csv of unihan.
    unihan_tabular/process.py

    # unit tests to verify behavior / consistency of builder
    tests/*

    # python 2/3 compatibility module
    unihan_tabular/_compat.py

    # utility / helper functions
    unihan_tabular/util.py

.. _MIT: http://opensource.org/licenses/MIT
.. _API: http://cihai.readthedocs.org/en/latest/api.html
.. _UNIHAN: http://www.unicode.org/charts/unihan.html
.. _create an issue: https://github.com/cihai/unihan-tabular/issues/new
.. _Data Package: http://frictionlessdata.io/data-packages/
.. _pyyaml: http://pyyaml.org/

.. |pypi| image:: https://img.shields.io/pypi/v/unihan-tabular.svg
    :alt: Python Package
    :target: http://badge.fury.io/py/unihan-tabular

.. |build-status| image:: https://img.shields.io/travis/cihai/unihan-tabular.svg
   :alt: Build Status
   :target: https://travis-ci.org/cihai/unihan-tabular

.. |coverage| image:: https://codecov.io/gh/cihai/unihan-tabular/branch/master/graph/badge.svg
    :alt: Code Coverage
    :target: https://codecov.io/gh/cihai/unihan-tabular

.. |license| image:: https://img.shields.io/github/license/cihai/unihan-tabular.svg
    :alt: License 

.. |docs| image:: https://readthedocs.org/projects/unihan-tabular/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/unihan-tabular/
