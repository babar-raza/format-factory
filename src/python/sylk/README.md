# Format Factory — SYLK

Parse and write SYLK (Symbolic Link Format) spreadsheet files with Format Factory.

## Installation

```
pip install aspose-format-factory-sylk
```

## Quick Start

```python
from sylk import SylkDocument, load_sylk, set_cell_value

# Class-based API (primary)
doc = SylkDocument.from_file("spreadsheet.slk")
print(doc.rows, doc.cells)

# File-based edit API
set_cell_value("input.slk", "output.slk", row=1, col=1, value="Updated")
```

## Features

- Parse SYLK (.slk) files
- Access cell data by row/column coordinates
- File-based cell editing and write
- Export to CSV

## License

Apache-2.0
