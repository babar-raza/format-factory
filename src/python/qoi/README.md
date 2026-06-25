# Format Factory — QOI

Parse QOI (Quite OK Image Format) files with Format Factory.

## Installation

```
pip install aspose-format-factory-qoi
```

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

Apache-2.0
