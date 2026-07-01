# Format Factory — PBM

Parse and write PBM (Portable Bitmap) image files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-01T19:59:02+00:00 source=package-metadata -->
```bash
pip install format-factory-pbm
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from pbm import PbmImage, load_pbm, write_pbm

# Class-based API (primary)
img = PbmImage.from_file("image.pbm")
print(img.width, img.height, img.format)

# Function API
model = load_pbm("image.pbm")
write_pbm(model, "output.pbm")
```

## Features

- Parse PBM P1 (ASCII) and P4 (binary) formats
- Access pixel data, dimensions, and metadata
- Write PBM output
- Security guards: 64 MB file size, 65536 dimension limits

## License

<!-- BEGIN:README-LICENSE generated=2026-07-01T19:59:02+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-01T19:59:02+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Portable Bitmap (PBM / Netpbm) |
| Track | python |
| Package | format-factory-pbm |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Jef Poskanzer (Netpbm project) Netpbm PBM specification (1988) |
| QName coverage | 3/3 implemented |
| Source files | 18 |
| Test files | 66 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-01T19:59:02+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
