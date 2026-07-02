# Format Factory — XCF

Parse XCF (GIMP native format) image files with Format Factory.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-07-02T16:00:11+00:00 source=package-metadata -->
```bash
pip install format-factory-xcf
```
<!-- END:README-INSTALLATION -->

## Quick Start

```python
from xcf import XcfImage, load_xcf

# Class-based API (primary)
img = XcfImage.from_file("image.xcf")
print(img.width, img.height, img.layer_names)

# Function API
model = load_xcf("image.xcf")
print(model["width"], model["height"], model["layer_count"])
```

## Features

- Parse XCF files (GIMP internal format)
- Access image dimensions, layer names, and channel data
- Analytics: layer count, canvas area, orientation

## License

<!-- BEGIN:README-LICENSE generated=2026-07-02T16:00:11+00:00 source=package-metadata -->
Apache-2.0
<!-- END:README-LICENSE -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-07-02T16:00:11+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | GIMP Native Image Format |
| Track | python |
| Package | format-factory-xcf |
| Version | 0.1.0 |
| License | Apache-2.0 |
| Python | >=3.9 |
| .NET | unknown |
| Spec | GIMP Development Team XCF v011 (GIMP 2.10+) |
| QName coverage | 4/4 implemented |
| Source files | 17 |
| Test files | 73 |
<!-- END:README-PACKAGE_INFO -->

## Public API

<!-- BEGIN:README-PUBLIC_API generated=2026-07-02T16:00:11+00:00 source=src-python-init -->
- `(dynamic)`
<!-- END:README-PUBLIC_API -->
