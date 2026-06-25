# Format Factory — ODT

Parse and write ODT (OpenDocument Text) files with Format Factory.

## Installation

```
pip install aspose-format-factory-odt
```

## Quick Start

```python
from odt import OdtDocument, parse_odt, write_odt, odt_from_text

# Class-based API (primary)
doc = OdtDocument.from_file("document.odt")
print(doc.paragraph_count, doc.paragraphs[0])

# Create a new document from text
odt_from_text("Hello, Format Factory!", "output.odt")

# Roundtrip
model = parse_odt("document.odt")
write_odt(model["paragraphs"], "copy.odt")
```

## Features

- Parse ODT files (ODF 1.3 text document format)
- Access paragraphs and document structure
- Write ODT output

## License

Apache-2.0
