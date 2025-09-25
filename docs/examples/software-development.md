(software-development)=

# Software Development

UNIHAN-ETL can be a powerful tool for software developers building applications that require Chinese character data.

## Dictionary Applications

This example demonstrates how to extract and structure UNIHAN data for a dictionary application:

```{literalinclude} ../../tests/examples/test_software_dev.py
:language: python
:linenos:
:caption: Dictionary application example
```

## Tips for Software Development

- **Selective Field Loading**: Only load the fields your application needs to reduce memory usage
- **Error Handling**: Be sure to handle cases where data may be strings, lists, or other formats
- **Data Transformation**: Convert raw UNIHAN data into application-specific structures
- **Unicode Support**: Ensure your application correctly handles Unicode for proper character display

## Related Projects

If you're developing software with Chinese character data, also consider checking out:

- [cihai](https://cihai.git-pull.com/): A unified CJK (Chinese, Japanese, Korean) library for Python
- [libUnihan](https://github.com/cihai/libUnihan): C library for UNIHAN data access
