(advanced-api)=

# Advanced API Usage

UNIHAN-ETL provides advanced API features for more sophisticated applications and integrations.

## Advanced API Features

This example demonstrates more complex usage of the UNIHAN-ETL API:

```{literalinclude} ../../tests/examples/test_advanced_api.py
:language: python
:linenos:
:caption: Advanced API usage
```

## API Development

For developers extending or integrating with UNIHAN-ETL:

```{literalinclude} ../../tests/examples/test_api_development.py
:language: python
:linenos:
:caption: API development and extension
```

## Advanced Configuration

The UNIHAN-ETL API allows for detailed configuration to meet specific requirements:

```python
# Conceptual example of advanced configuration
from unihan_etl.core import Packager

# Create a packager with advanced configuration
packager = Packager({
    # Specify fields to include
    "fields": ["kDefinition", "kCantonese", "kMandarin", "kTotalStrokes"],
    
    # Configure output formatting
    "format": "json",
    "destination": "/path/to/output/file.json",
    
    # Set download options
    "download": True,
    "work_dir": "/path/to/cache",
    
    # Configure data processing
    "expand": True,  # Expand delimited values into lists
    "prune_empty": True,  # Remove fields with empty values
})

# Execute the processing pipeline
packager.process()
```

## Custom Processing Pipelines

Create custom processing pipelines for specialized applications:

```python
# Conceptual example of a custom processing pipeline
def custom_unihan_pipeline(options):
    # Create the packager
    packager = Packager(options)
    
    # Download data if needed
    if not packager.has_data():
        packager.download()
    
    # Get raw data
    raw_data = packager.get_raw_data()
    
    # Apply custom preprocessing
    preprocessed_data = custom_preprocess(raw_data)
    
    # Apply standard normalization
    normalized_data = packager.normalize(preprocessed_data)
    
    # Apply custom post-processing
    processed_data = custom_postprocess(normalized_data)
    
    # Return processed data
    return processed_data
```

## Tips for Advanced API Usage

- Study the API documentation thoroughly before implementing advanced features
- Create reusable utilities for common advanced operations
- Test API usage with small datasets before scaling to full UNIHAN data
- Consider performance implications when designing custom processing pipelines
- Add proper error handling for robust applications
