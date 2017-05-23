.. _about:

====================
About unihan-tabular
====================

Handles encoding
----------------

Dealing with unicode encodings can be cumbersome across platforms.

Python 2 and 3
--------------

Designed and tested to work across Python versions.

Customizable output
-------------------

Formats
"""""""

- CSV
- JSON
- YAML (requires `pyyaml <http://pyyaml.org/>`_)
- Python dict (via :ref:`API`)

Structured output
"""""""""""""""""

*JSON, YAML, and python dict only*

Support for structured output of information in fields. unihan-tabular
refers to this as *expansion*.

Users can opt-out via ``--no-expand``. This will preserve the values in
each field as they are in the raw database.

Filters out empty values by default, opt-out via ``--no-prune``.

Filtering
"""""""""

Support for filtering by fields and files.
