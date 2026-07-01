# Format Factory — PGM

Parse and write PGM (Portable Graymap) image files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-01T15:33:04+00:00 source=package-metadata -->
```bash
pip install format-factory-pgm
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from pgm import PgmImage, load_pgm, write_pgm

# Class-based API (primary)
img = PgmImage.from_file("image.pgm")
print(img.width, img.height, img.maxval)

# Function API
model = load_pgm("image.pgm")
write_pgm(model, "output.pgm")
```

## Features

- Parse PGM P2 (ASCII) and P5 (binary) formats
- Access pixel data, dimensions, and max value
- Write PGM output
- Security guards: 64 MB file size limit

## License

<!-- BEGIN:README-LICENSE generated=2026-07-01T15:33:04+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-01T15:33:04+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Portable Graymap (PGM / Netpbm) |
| Track | python |
| Package | format-factory-pgm |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Jef Poskanzer (Netpbm project) Netpbm PGM specification (1988) |
| QName coverage | 3/3 implemented |
| Source files | 15 |
| Test files | 59 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-01T15:33:04+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
