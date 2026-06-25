# Format Factory — PGM

Parse and write PGM (Portable Graymap) image files with Format Factory.

## Installation

```
pip install aspose-format-factory-pgm
```

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

Apache-2.0
