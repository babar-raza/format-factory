# Format Factory — xliff

Parse, edit, and write OASIS XLIFF 2.1 (.xliff, .xlf) localization files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-15T19:25:43+00:00 source=package-metadata -->
```bash
pip install format-factory-xliff
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from xliff.xliff_codec import load_xliff, write_xliff

model = load_xliff("translation.xliff")
for f in model["files"]:
    for unit in f["units"]:
        print(unit["segment"]["source"], "->", unit["segment"]["target"])

# Mutate a segment's translation state, then write back
model["files"][0]["units"][0]["segment"]["state"] = "reviewed"
write_xliff(model, "translation-reviewed.xliff")
```

## Features

- Structural inline markup preservation (`pc`/`sc`/`ec`/`ph`/`mrk`) — survives load→edit→save without flattening
- Segment `state` write-back (translated/reviewed/final, etc.)
- Notes preservation (file-level and unit-level)
- Group hierarchy preservation, including nested groups
- Core file/unit/segment structure with source/target language

**Scope note:** optional OASIS modules and XLIFF 1.2 write support remain out of scope for this pass. See `reports/spec-coverage/xliff-deferred.json`.

## License

<!-- BEGIN:README-LICENSE generated=2026-07-15T19:25:43+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-15T19:25:43+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | XLIFF (XML Localisation Interchange File Format) |
| Track | python |
| Package | format-factory-xliff |
| Version | 0.1.0.dev0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | OASIS XLIFF 2.1 |
| QName coverage | 3/3 implemented |
| Source files | 16 |
| Test files | 7 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-15T19:25:43+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
