# Format Factory — ODS

Parse and write ODS (OpenDocument Spreadsheet) files with Format Factory.

## Installation

```
pip install aspose-format-factory-ods
```

## Quick Start

```python
from ods import OdsDocument, parse_ods, write_ods

# Class-based API (primary)
doc = OdsDocument.from_file("spreadsheet.ods")
print(doc.sheet_count, doc.sheets[0].name)

# Edit and save
write_ods(doc.to_dict(), "output.ods")
```

## Features

- Parse ODS files (ODF 1.3 spreadsheet format)
- Access sheets, rows, and cells
- Write ODS output

## License

Apache-2.0
