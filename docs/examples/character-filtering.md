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

```python
# Example of filtering by grade level (conceptual example)
options = {
    "fields": ["kGradeLevel", "kTotalStrokes", "kDefinition"],
}
packager = Packager(options)
# ... process data ...
elementary_chars = [item for item in data if item.get("kGradeLevel") in ["1", "2", "3"]]
```

### Simplified/Traditional Pairs

Identify characters with simplified variants:

```python
# Example of identifying simplified/traditional pairs (conceptual example)
options = {
    "fields": ["kSimplifiedVariant", "kTraditionalVariant"],
}
packager = Packager(options)
# ... process data ...
simplified_pairs = [item for item in data if "kSimplifiedVariant" in item or "kTraditionalVariant" in item]
```

## Tips for Character Filtering

- Carefully select the fields you need to minimize memory usage
- Consider processing data in batches for very large datasets
- Create reusable filtering functions for complex criteria
- Validate filtered results to ensure they meet your requirements
