# Format Factory — TOML

Parse and write TOML (Tom's Obvious Minimal Language) configuration files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:27+00:00 source=package-metadata -->
```bash
pip install format-factory-toml
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from toml import TomlDocument, load_toml, write_toml

# Class-based API (primary)
doc = TomlDocument.from_file("config.toml")
print(doc.key_count, doc.section_count)

# Function API
model = load_toml("config.toml")
model["new_key"] = "new_value"
write_toml(model, "output.toml")
```

## Features

- Parse TOML files
- Access keys and sections
- Write modified TOML output
- Analytics: key count, section depth, value types

## License

<!-- BEGIN:README-LICENSE generated=2026-06-28T08:14:27+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:27+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Tom's Obvious, Minimal Language |
| Track | python |
| Package | format-factory-toml |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | TOML Project v1.0.0 |
| QName coverage | 3/3 implemented |
| Source files | 17 |
| Test files | 58 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-06-28T08:14:27+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
