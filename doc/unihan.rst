.. _unihan:

============
About UNIHAN
============

.. seealso::

    - `Wikipedia article <https://en.wikipedia.org/wiki/Han_unification>`_
    - `Documentation of the UNIHAN Database <http://www.unicode.org/reports/tr38/>`_

What is UNIHAN?
---------------

The *Unicode Consortium*, authors of the `Unicode Standard`_, provide a standard
of consistently representing and encoding the world's writing systems.

UNIHAN, short for `Han unification`_, is the effort of the consortium map CJK
languages into unified characters. A very time-consuming and painstaking
challenge.

The advantage that UNIHAN provides to east asian researchers, including
sinologists and japanologists, linguists, anaylsts, language learners, and
hobbyists cannot be understated. Despite its use under the hood in many
applications and websites, it is underrepresented and often overlooked as a
source of reliable information. It's potential uses are not readily
understood without reading into the standard and wrangling the data.

It isn't readily accessible in data form for developers. Even some of the public
implementers of UNIHAN haven't fully exploited its potential.

.. _Unicode Standard: https://en.wikipedia.org/wiki/Unicode
.. _Han unification: https://en.wikipedia.org/wiki/Han_unification

The problem
-----------

It's difficult to readily take advantage of UNIHAN database in its
raw form.

UNIHAN comprises over 20 MB of character information, separated
across multiple files. Within these files is *90* fields, spanning 8
general categories of data. Within some of fields, there are specific
considerations to take account of to use the data correctly, for instance:

UNIHAN's values place references to its own codepoints, such as
*kDefinition*::

    U+3400       kDefinition     (same as U+4E18 丘) hillock or mound

And also by spaces, such as in *kCantonese*::

    U+342B       kCantonese      gun3 hung1 zung1

And by spaces which specify different sources, like *kMandarin*, "When
there are two values, then the first is preferred for zh-Hans (CN) and the
second is preferred for zh-Hant (TW). When there is only one value, it is
appropriate for both."::

    U+7E43        kMandarin       běng bēng

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

Data could be exported to a CSV, which unihan-tabular currently
supports. Users would have to still be left to their own devices handle
delimited values and structured information that's held within.

Also, CSV does not support structured information. Another format that
supports needs to be found.

Even then, users may not want an export that handles the structured
output of fields. So if a tool exists, it should be configurable, users
enabling the export to keep values of ``gun3 hung1 zung1`` pristine without
turning it into list form.
