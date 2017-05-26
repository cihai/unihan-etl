.. _about:

================
About unihan-etl
================

unihan-etl provides configurable, self-serve data exports of the
:ref:`UNIHAN` database.

Retrieval
---------

unihan-etl will download and cache the raw database files for the
user.

Handles encoding
----------------

Dealing with unicode encodings can be cumbersome across platforms.
unihan-etl deals with handling output encoding issues that could
come up if you were to try to export the data yourself.

Python 2 and 3
--------------

Designed and tested to work across Python versions. View the `travis test
matrix <https://travis-ci.org/cihai/unihan-etl>`_ for what this
software is tested against.

Customizable output
-------------------

Formats
"""""""

- CSV
- JSON
- YAML (requires `pyyaml <http://pyyaml.org/>`_)
- Python dict (via :ref:`api`)

Structured output
"""""""""""""""""

*JSON, YAML, and python dict only*

Support for structured output of information in fields. unihan-etl
refers to this as *expansion*.

Users can opt-out via ``--no-expand``. This will preserve the values in
each field as they are in the raw database.

Filters out empty values by default, opt-out via ``--no-prune``.

Filtering
"""""""""

Support for filtering by fields and files.

To specify which fields to output, use ``-f`` / ``--fields`` and separate
them in spaces. ``-f kDefinition kCantonese kHanyuPinyin``.

For files, ``-i`` / ``--input-files``. Example: ``-i
Unihan_DictionaryLikeData.txt Unihan_Readings.txt``.
