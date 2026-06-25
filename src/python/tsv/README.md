# Format Factory — TSV

Parse and write TSV (tab-separated values) files with Format Factory.

## Installation

```
pip install aspose-format-factory-tsv
```

## Quick Start

```python
from tsv import TsvDocument, parse_tsv_strict, write_tsv

# Class-based API (primary)
doc = TsvDocument.from_file("data.tsv")
print(doc.row_count, doc.column_count, doc.headers)

# Function API
model = parse_tsv_strict("data.tsv")
rows = model["rows"]  # list of list[str]
rows.append(["Alice", "Engineering", "95000"])
write_tsv(rows, "output.tsv", headers=model["headers"])
```

## Features

- Parse TSV files with tab delimiter
- Header-aware access (headers, rows, cell values)
- Write TSV output

## License

Apache-2.0
