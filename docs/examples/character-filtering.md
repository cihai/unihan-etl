(character-filtering)=

# Character Filtering & Selection

UNIHAN-ETL provides powerful ways to filter and select specific Chinese characters based on various criteria.

## Character Filtering

This example demonstrates how to filter characters based on specific properties:

```{literalinclude} ../../tests/examples/test_character_filtering.py
:language: python
:linenos:
:caption: Filtering characters by properties
```

## Advanced Selection Techniques

UNIHAN-ETL allows you to create sophisticated queries to select characters with specific characteristics. 
This is especially useful for:

- Creating frequency-based character lists for language learning
- Selecting characters with specific components or radicals
- Identifying simplified/traditional character pairs
- Filtering characters by grade level or usage frequency

## Common Filtering Use Cases

### Educational Materials

Filter characters by grade level to create age-appropriate educational materials:

```{literalinclude} ../../tests/examples/test_educational_filtering.py
:language: python
:linenos:
:caption: Filtering characters by grade level
```

### Simplified/Traditional Pairs

Identify characters with simplified variants:

```{literalinclude} ../../tests/examples/test_simplified_traditional.py
:language: python
:linenos:
:caption: Identifying simplified/traditional character pairs
```

## Tips for Character Filtering

- Carefully select the fields you need to minimize memory usage
- Consider processing data in batches for very large datasets
- Create reusable filtering functions for complex criteria
- Validate filtered results to ensure they meet your requirements
