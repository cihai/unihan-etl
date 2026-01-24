(custom-fields)=

# Custom Fields

UNIHAN-ETL allows you to extend beyond the standard UNIHAN fields by creating custom fields through data transformation.

## Adding Custom Fields

This example demonstrates how to add your own custom fields to UNIHAN data:

```{literalinclude} ../../tests/examples/test_custom_fields.py
:language: python
:linenos:
:caption: Custom fields example
```

## Use Cases for Custom Fields

Custom fields can enhance UNIHAN data in many ways:

- **Difficulty Assessment**: Create composite scores based on stroke count, frequency, etc.
- **Learning Progression**: Add sequential IDs for optimal learning order
- **Application-Specific Tags**: Add domain-specific categorization 
- **Cross-References**: Add links to related characters, similar meanings, etc.
- **Metadata**: Add timestamps, version indicators, or other administrative data

## Tips for Creating Custom Fields

- **Deterministic Functions**: Ensure custom field generation is deterministic for consistent results
- **Documentation**: Document the meaning and calculation method for each custom field
- **Data Validation**: Validate custom fields to ensure they contain expected values
- **Performance**: For large datasets, consider optimizing your custom field functions
- **Storage Strategy**: Decide whether to calculate custom fields on-the-fly or store them persistently
