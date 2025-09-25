(stroke-order)=

# Stroke Order & Character Writing

UNIHAN-ETL provides data that can be used for applications teaching stroke order and character writing.

## Stroke Order Information

This example demonstrates how to access stroke count and other writing-related data:

```{literalinclude} ../../tests/examples/test_stroke_order.py
:language: python
:linenos:
:caption: Accessing stroke order information
```

## Character Writing Applications

UNIHAN-ETL data can be used to create character writing applications that:

1. Display correct stroke count
2. Show radical composition
3. Group characters by visual similarity
4. Present characters in a logical learning sequence

## Radical-Based Learning

Organize characters by their radical components for systematic learning:

```{literalinclude} ../../tests/examples/test_radical_groups.py
:language: python
:linenos:
:caption: Grouping characters by radical
```

## Progressive Difficulty

Create a learning progression based on stroke count and frequency:

```{literalinclude} ../../tests/examples/test_learning_progression.py
:language: python
:linenos:
:caption: Creating a character learning progression
```

## Tips for Stroke Order Applications

- Supplement UNIHAN data with stroke sequence information from other sources
- Consider character complexity when designing learning progressions
- Group visually similar characters to help learners distinguish between them
- Include information about common errors in character writing
- Provide visual and interactive feedback for learners
