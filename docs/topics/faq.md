(faq)=

# Frequently Asked Questions

## Why are some fields, e.g. [kTotalStrokes](https://www.unicode.org/reports/tr38/#kTotalStrokes), in lists when there's seemingly no multi-value data?

The word back from the developers of {ref}`UNIHAN <unihan>` is they keep
some fields multi-valued for future use.

> Apparently at the moment there is only one record with two values for
> the kTotalStrokes field in the Unihan database. However, the maintainers
> of the data intend to populate the kTotalStrokes field as needed in the
> future, and as documented in UAX #38.
>
> May 30, 2017 (Unicode 9.0)

unihan-etl handles these fields consistently, following the documentation
in the database.
