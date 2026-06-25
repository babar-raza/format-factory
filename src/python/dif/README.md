# Format Factory — DIF

Parse and write DIF (Data Interchange Format) files with Format Factory.

## Installation

```
pip install aspose-format-factory-dif
```

## Quick Start

```python
from dif import DifDocument, load_dif, write_dif

# Class-based API (primary)
doc = DifDocument.from_file("spreadsheet.dif")
print(doc.spec_qname, doc.rows, doc.vectors, doc.tuples)

# Function API
model = load_dif("spreadsheet.dif")
write_dif(model, "output.dif")
```

## Features

- Parse DIF files (vectors/tuples format)
- Access rows as `DifCell` objects
- Write modified DIF output

## License

Apache-2.0
