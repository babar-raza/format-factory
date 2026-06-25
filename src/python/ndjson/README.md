# Format Factory — NDJSON

Parse and write NDJSON (Newline-Delimited JSON) files with Format Factory.

## Installation

```
pip install aspose-format-factory-ndjson
```

## Quick Start

```python
from ndjson import NdjsonDocument, load_ndjson, write_ndjson

# Class-based API (primary)
doc = NdjsonDocument.from_file("records.ndjson")
print(doc.record_count, doc.get_record(0))

# Function API
records = load_ndjson("records.ndjson")
records.append({"id": 99, "name": "new"})
write_ndjson(records, "output.ndjson")
```

## Features

- Parse NDJSON files (one JSON object per line)
- Query records, fields, and schema uniformity
- Write NDJSON output
- Analytics: null ratio, value variance, type uniformity

## License

Apache-2.0
