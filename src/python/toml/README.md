# Format Factory — TOML

Parse and write TOML (Tom's Obvious Minimal Language) configuration files with Format Factory.

## Installation

```
pip install aspose-format-factory-toml
```

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

Apache-2.0
