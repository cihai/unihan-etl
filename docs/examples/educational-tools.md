(educational-tools)=

# Educational Tools

UNIHAN-ETL provides rich data for educational applications focused on Chinese character learning.

## Character Learning Application

This example demonstrates how to extract data for an educational application:

```{literalinclude} ../../tests/examples/test_educational_tools.py
:language: python
:linenos:
:caption: Educational application example
```

## Educational Applications

UNIHAN-ETL is ideal for creating:

- **Character Learning Apps**: Create interactive apps for learning Chinese characters
- **Flashcard Systems**: Generate flashcards with character information
- **Language Curriculum Materials**: Build grade-appropriate character lists
- **Cross-language Comparisons**: Compare character usage across Chinese, Japanese, and Korean

## Educational Fields

Key UNIHAN fields useful for educational tools include:

| Field | Description |
|-------|-------------|
| kTotalStrokes | Number of strokes needed to write the character |
| kGradeLevel | School grade level (in the PRC) when the character is typically taught |
| kDefinition | English definition of the character |
| kMandarin | Mandarin pronunciation(s) |
| kCantonese | Cantonese pronunciation(s) |
| kJapaneseOn | Japanese On (Sino-Japanese) reading(s) |
| kJapaneseKun | Japanese Kun (native Japanese) reading(s) |
| kKorean | Korean pronunciation(s) |
