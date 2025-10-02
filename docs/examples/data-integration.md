(data-integration)=

# Data Integration

UNIHAN-ETL simplifies the process of integrating UNIHAN data with various database systems and data pipelines.

## SQLite Database Integration

This example shows how to extract UNIHAN data and store it in a SQLite database:

```{literalinclude} ../../tests/examples/test_data_integration.py
:language: python
:linenos:
:caption: SQLite database integration example
```

## Integration with Other Systems

UNIHAN-ETL can be used to prepare data for various systems:

- **SQL Databases**: MySQL, PostgreSQL, SQLite
- **NoSQL Databases**: MongoDB, CouchDB
- **Analytics Platforms**: Hadoop, Spark
- **Web Applications**: RESTful APIs, GraphQL

## Tips for Data Integration

- **Select Only Needed Fields**: Reduce data size by selecting only required fields
- **Consistent Data Types**: Handle type conversions before inserting into databases
- **Incremental Updates**: Consider using UNIHAN-ETL to perform differential updates
- **Proper Indexing**: Index frequently queried fields in your database for better performance
- **Character Encoding**: Ensure your database properly supports UTF-8 encoding
