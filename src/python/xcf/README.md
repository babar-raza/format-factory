# Format Factory — XCF

Parse XCF (GIMP native format) image files with Format Factory.

## Installation

```
pip install aspose-format-factory-xcf
```

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

Apache-2.0
