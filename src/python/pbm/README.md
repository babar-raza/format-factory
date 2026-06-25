# Format Factory — PBM

Parse and write PBM (Portable Bitmap) image files with Format Factory.

## Installation

```
pip install aspose-format-factory-pbm
```

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

Apache-2.0
