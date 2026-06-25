# PBM Python API Reference

**Package:** `aspose-format-factory-pbm`
**Version:** 0.1.0
**Format:** Portable Bitmap (PBM) — Netpbm P1/P4
**Spec:** Netpbm specification (1-bit black-and-white raster)

---

## Installation

```bash
pip install aspose-format-factory-pbm
```

```python
import pbm
```

---

## Core Functions

### `parse_pbm_strict`

```python
def parse_pbm_strict(file_path: str | Path) -> PbmImage
```

Parse a PBM file (P1 ASCII or P4 binary) and return a `PbmImage` object.
Raises `PbmInvalidMagicError`, `PbmInvalidHeaderError`, `PbmSizeError`, or `PbmDecodeError` on failure.

### `parse_pbm`

```python
def parse_pbm(file_path: str | Path) -> dict[str, Any]
```

Parse a PBM file and return a dictionary with keys: `magic`, `width`, `height`, `pixels`.

### `probe_pbm`

```python
def probe_pbm(file_path: str | Path) -> dict[str, Any]
```

Probe a PBM file for header metadata without decoding pixel data. Returns `magic`, `width`, `height`, `file_size`.

### `write_pbm`

```python
def write_pbm(pixels: list[list[int]], width: int, height: int, dest_path: str | Path, *, binary: bool = True) -> dict[str, Any]
```

Write pixel data to a PBM file. `pixels` is a list of rows; each row is a list of 0/1 ints (0=white, 1=black).
Set `binary=False` for P1 (ASCII) output. Returns metadata dict.

---

## Domain Model

### `PbmImage`

```python
@dataclass
class PbmImage:
    spec_qname: ClassVar[str] = "pbm:image"
    path: Path
    magic: str           # "P1" or "P4"
    width: int
    height: int
    pixels: list[list[int]]  # row-major; 0=white, 1=black
```

---

## Pixel Analytics

### Dimensions

```python
def get_dimensions(file_path) -> tuple[int, int]   # (width, height)
def pbm_dimensions(file_path) -> dict               # {"width": int, "height": int}
def pixel_count(file_path) -> int                   # total pixels = width * height
def pbm_area(file_path) -> int                      # alias for pixel_count
def pbm_perimeter(file_path) -> int                 # 2*(width + height)
def aspect_ratio(file_path) -> float                # width / height
def pbm_megapixels(file_path) -> float              # pixel_count / 1_000_000
```

### Black/White Counts

```python
def count_black(file_path) -> int
def count_white(file_path) -> int
def pbm_black_pixel_count(file_path) -> int
def pbm_white_pixel_count(file_path) -> int
def pbm_black_pixel_ratio(file_path) -> float       # 0.0–1.0
def pbm_white_pixel_ratio(file_path) -> float       # 0.0–1.0
def pbm_black_density(file_path) -> float           # alias for black_pixel_ratio
def pbm_white_density(file_path) -> float           # alias for white_pixel_ratio
def pbm_has_any_black(file_path) -> bool
def pbm_has_any_white(file_path) -> bool
def pbm_all_black(file_path) -> bool
def pbm_all_white(file_path) -> bool
def pbm_is_uniform(file_path) -> bool               # all pixels same value
```

### Row/Column Analytics

```python
def pbm_row_count(file_path) -> int
def pbm_column_count(file_path) -> int
def pbm_row_black_counts(file_path) -> list[int]
def pbm_column_black_counts(file_path) -> list[int]
def pbm_max_row_black_count(file_path) -> int
def pbm_min_row_black_count(file_path) -> int
```

### Shape Properties

```python
def pbm_is_square(file_path) -> bool
def pbm_is_landscape(file_path) -> bool
def pbm_is_portrait(file_path) -> bool
def pbm_is_tall(file_path) -> bool
def pbm_is_wide(file_path) -> bool
def pbm_is_binary(file_path) -> bool                # always True for PBM
def pbm_aspect_ratio(file_path) -> float
def pbm_dimension_ratio(file_path) -> float
def pbm_min_dimension(file_path) -> int
def pbm_max_dimension(file_path) -> int
def pbm_diagonal(file_path) -> float                # sqrt(w^2 + h^2)
def pbm_pixel_density(file_path) -> float
def image_pixel_stats(file_path) -> dict[str, Any]  # comprehensive stats dict
```

---

## Transform Operations

```python
def flip_horizontal(file_path, dest_path) -> dict[str, Any]
def invert(file_path, dest_path) -> dict[str, Any]    # swap black/white
def rotate_90(file_path, dest_path) -> dict[str, Any]
def crop(file_path, dest_path, x, y, w, h) -> dict[str, Any]
def scale_nearest(file_path, dest_path, factor: int) -> dict  # nearest-neighbor scale
```

---

## Conversion

```python
# pbm.pbm_to_pgm module
def convert_pbm_to_pgm(file_path, dest_path) -> dict[str, Any]  # PBM -> PGM (grayscale)

# pbm.pbm_to_ppm module
def convert_pbm_to_ppm(file_path, dest_path) -> dict[str, Any]  # PBM -> PPM (color)
```

---

## Exceptions

```python
class PbmError(Exception): ...
class PbmInvalidMagicError(PbmError): ...    # magic != "P1"/"P4"
class PbmInvalidHeaderError(PbmError): ...  # malformed header
class PbmSizeError(PbmError): ...           # file too large or dimensions unreasonable
class PbmDecodeError(PbmError): ...         # pixel data decode failure
```

---

## Security

- File size guard enforced: raises `PbmSizeError` for files exceeding safe limits
- No external XML/DTD processing; pure binary/text pixel data only
- Strict magic-byte validation before any decode attempt

---

## Quickstart

```python
import pbm

# Parse and inspect
img = pbm.parse_pbm_strict("samples/by-format/pbm/valid/2x2-checker.pbm")
print(img.width, img.height, img.magic)

# Pixel stats
print(pbm.count_black("samples/by-format/pbm/valid/2x2-checker.pbm"))
print(pbm.get_dimensions("samples/by-format/pbm/valid/2x2-checker.pbm"))

# Write
pbm.write_pbm([[0, 1], [1, 0]], 2, 2, "/tmp/out.pbm")
```
