# Format Factory — QOI

Parse QOI (Quite OK Image Format) files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-01T21:01:42+00:00 source=package-metadata -->
```bash
pip install format-factory-qoi
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from qoi import QoiImage, load_qoi

# Class-based API (primary)
img = QoiImage.from_file("image.qoi")
print(img.width, img.height, img.channels, img.colorspace)

# Function API
model = load_qoi("image.qoi")
print(model["width"], model["height"])
```

## Features

- Parse QOI files (lossless image format)
- Access dimensions, channels, and colorspace
- Analytics: total brightness, pixel density

## License

<!-- BEGIN:README-LICENSE generated=2026-07-01T21:01:42+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-01T21:01:42+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Quite OK Image Format |
| Track | python |
| Package | format-factory-qoi |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | Dominic Szablewski / phoboslab QOI 1.0 (November 2021) |
| QName coverage | 3/3 implemented |
| Source files | 17 |
| Test files | 42 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-01T21:01:42+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
