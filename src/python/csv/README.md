# Format Factory — CSV

Parse, query, and write CSV (comma-separated values) files with Format Factory.

## Installation

```
pip install aspose-format-factory-csv
```

## Quick Start

```python
from csv_format import CsvDocument, parse_csv_strict, write_csv_to_file

# Class-based API (primary)
doc = CsvDocument.from_file("data.csv")
print(doc.row_count, doc.column_count, doc.headers)

# Function API
model = parse_csv_strict("data.csv")
write_csv_to_file(model["rows"], "output.csv", headers=model["headers"])
```

## Features

- Parse CSV files with delimiter detection
- Query rows, columns, and cell values
- Header-aware access (`get_column_names()`, `get_cell_value()`)
- Write CSV output

## License

Apache-2.0
