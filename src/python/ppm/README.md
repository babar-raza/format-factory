# Format Factory — PPM

Parse and write PPM (Portable Pixmap) color image files with Format Factory.

## Installation

```
pip install aspose-format-factory-ppm
```

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

Apache-2.0
