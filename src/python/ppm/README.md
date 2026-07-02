# Format Factory — PPM

Parse and write PPM (Portable Pixmap) color image files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-02T13:18:27+00:00 source=package-metadata -->
```bash
pip install format-factory-ppm
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from ppm import PpmImage, load_ppm, write_ppm

# Class-based API (primary)
img = PpmImage.from_file("image.ppm")
print(img.width, img.height, img.maxval)

# Function API
model = load_ppm("image.ppm")
write_ppm(model, "output.ppm")
```

## Features

- Parse PPM P3 (ASCII) and P6 (binary) formats
- Access RGB pixel data, dimensions, and max value
- Write PPM output
- Security guards: 64 MB file size limit

## License

<!-- BEGIN:README-LICENSE generated=2026-07-02T13:18:27+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-02T13:18:27+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Portable Pixmap (PPM / Netpbm) |
| Track | python |
| Package | format-factory-ppm |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Jef Poskanzer (Netpbm project) Netpbm PPM specification (1988, public domain) |
| QName coverage | 3/3 implemented |
| Source files | 16 |
| Test files | 82 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-02T13:18:27+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
