# Format Factory — NDJSON

Parse and write NDJSON (Newline-Delimited JSON) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:25+00:00 source=package-metadata -->
```bash
pip install format-factory-ndjson
```
<!-- END:README-INSTALLATION -->

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

<!-- BEGIN:README-LICENSE generated=2026-06-28T08:14:25+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:25+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Newline Delimited JSON |
| Track | python |
| Package | format-factory-ndjson |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Informal (ndjson.org) v1 |
| QName coverage | 2/2 implemented |
| Source files | 17 |
| Test files | 147 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-06-28T08:14:25+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
