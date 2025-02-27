(linguistic-analysis)=

# Linguistic & Research Analysis

UNIHAN-ETL provides valuable data for linguistic research and analysis of Chinese characters.

## Linguistic Analysis

This example demonstrates how to extract and analyze linguistic properties of characters:

```{literalinclude} ../../tests/examples/test_linguistic_analysis.py
:language: python
:linenos:
:caption: Linguistic analysis of characters
```

## Research Applications

UNIHAN-ETL can be used for academic research on Chinese characters:

```{literalinclude} ../../tests/examples/test_research_analysis.py
:language: python
:linenos:
:caption: Research analysis of characters
```

## Linguistic Research Applications

### Character Evolution Studies

Trace the historical development of characters across time:

```python
# Conceptual example of historical analysis
def analyze_historical_variants(character):
    # Find character data
    char_data = find_character_data(character)
    
    # Extract historical variant information
    variants = []
    if "kSemanticVariant" in char_data:
        variants.extend(char_data["kSemanticVariant"])
    if "kZVariant" in char_data:
        variants.extend(char_data["kZVariant"])
    if "kSpecializedSemanticVariant" in char_data:
        variants.extend(char_data["kSpecializedSemanticVariant"])
        
    return variants
```

### Cross-language Comparisons

Compare character usage across Chinese, Japanese, and Korean:

```python
# Conceptual example of cross-language analysis
def compare_cjk_readings(character):
    # Find character data
    char_data = find_character_data(character)
    
    # Extract readings in different languages
    return {
        "mandarin": char_data.get("kMandarin", ""),
        "cantonese": char_data.get("kCantonese", ""),
        "japanese_on": char_data.get("kJapaneseOn", ""),
        "japanese_kun": char_data.get("kJapaneseKun", ""),
        "korean": char_data.get("kKorean", ""),
        "vietnamese": char_data.get("kVietnamese", "")
    }
```

## Tips for Linguistic Research

- Combine UNIHAN data with other linguistic resources for comprehensive analysis
- Consider the historical development of characters when analyzing variants
- Document your methodology clearly for academic reproducibility
- Validate findings against established linguistic research
- Use statistical methods to identify patterns in character usage and structure
