# PGM Python API Reference

**Package:** `aspose-format-factory-pgm`
**Version:** 0.1.0
**Format:** Portable Graymap (PGM) — Netpbm P2/P5
**Spec:** Netpbm specification (8-bit grayscale raster)

---

## Installation

```bash
pip install aspose-format-factory-pgm
```

```python
import pgm
```

---

## Core Functions

### `parse_pgm_strict`

```python
def parse_pgm_strict(file_path: str | Path) -> PgmImage
```

Parse a PGM file (P2 ASCII or P5 binary) and return a `PgmImage` object.
Raises `PgmInvalidMagicError`, `PgmInvalidHeaderError`, `PgmSizeError`, or `PgmDecodeError` on failure.

### `parse_pgm`

```python
def parse_pgm(file_path: str | Path) -> dict[str, Any]
```

Parse a PGM file and return a dictionary with keys: `magic`, `width`, `height`, `maxval`, `pixels`.

### `probe_pgm`

```python
def probe_pgm(file_path: str | Path) -> dict[str, Any]
```

Probe a PGM file for header metadata without decoding pixel data.
Returns `magic`, `width`, `height`, `maxval`, `file_size`.

### `write_pgm`

```python
def write_pgm(pixels: list[list[int]], width: int, height: int, maxval: int, dest_path: str | Path, *, binary: bool = True) -> dict[str, Any]
```

Write grayscale pixel data to a PGM file. `pixels` is a list of rows; each value is 0–`maxval`.
Set `binary=False` for P2 (ASCII) output.

---

## Domain Model

### `PgmImage`

```python
@dataclass
class PgmImage:
    spec_qname: ClassVar[str] = "pgm:image"
    path: Path
    magic: str           # "P2" or "P5"
    width: int
    height: int
    maxval: int          # max pixel value (typically 255)
    pixels: list[list[int]]  # row-major grayscale values
```

---

## Pixel Analytics

### Dimensions

```python
def get_dimensions(file_path) -> tuple[int, int]   # (width, height)
def pixel_count(file_path) -> int
def pgm_total_pixel_count(file_path) -> int
def pgm_area(file_path) -> int
def pgm_perimeter(file_path) -> int
def pgm_megapixels(file_path) -> float
def pgm_aspect_ratio(file_path) -> float
def pgm_dimension_ratio(file_path) -> float
def pgm_min_dimension(file_path) -> int
def pgm_max_dimension(file_path) -> int
def pgm_diagonal(file_path) -> float
```

### Brightness Statistics

```python
def average_gray(file_path) -> float
def min_max_gray(file_path) -> tuple[int, int]      # (min, max)
def pgm_min_pixel_value(file_path) -> int
def pgm_max_pixel_value(file_path) -> int
def pgm_average_brightness(file_path) -> float
def pgm_mean_brightness(file_path) -> float
def pgm_contrast_range(file_path) -> int            # max - min
def pgm_dynamic_range(file_path) -> int             # alias for contrast_range
def pgm_brightness_range(file_path) -> int
def pgm_median_pixel_value(file_path) -> int
def pgm_brightness_quartiles(file_path) -> dict[str, int]  # q1, q2, q3, q4
def pgm_pixel_sum(file_path) -> int
def pgm_brightness_ratio(file_path) -> float        # avg / maxval
def pgm_standard_deviation(file_path) -> float
def grayscale_variance(file_path) -> float
```

### Threshold Analytics

```python
def count_above_threshold(file_path, threshold: int) -> int
def pgm_bright_pixel_ratio(file_path, threshold: int = 128) -> float
def pgm_dark_pixel_count(file_path, threshold: int = 64) -> int
def pgm_zero_pixel_count(file_path) -> int
def pgm_saturated_pixel_count(file_path) -> int     # pixels at maxval
def pgm_nonzero_pixel_ratio(file_path) -> float
def pgm_has_any_saturated(file_path) -> bool
def pgm_has_any_zero(file_path) -> bool
def pgm_is_uniform(file_path) -> bool
def pgm_is_all_dark(file_path) -> bool
def pgm_is_all_bright(file_path) -> bool
def pgm_unique_value_count(file_path) -> int
```

### Shape Properties

```python
def pgm_is_square(file_path) -> bool
def pgm_is_landscape(file_path) -> bool
```

### Full Stats

```python
def image_pixel_stats(file_path) -> dict[str, Any]  # comprehensive stats dict
def histogram(file_path) -> dict[str, Any]           # pixel value histogram
```

---

## Transform Operations

```python
def flip_horizontal(file_path, dest_path) -> dict[str, Any]
def rotate_90(file_path, dest_path) -> dict[str, Any]
def normalize(file_path, dest_path, new_maxval: int = 255) -> dict[str, Any]
def threshold(file_path, dest_path, threshold_val: int, *, invert: bool = False) -> dict[str, Any]
```

---

## Conversion

```python
# pgm.pgm_to_ppm module
def convert_pgm_to_ppm(file_path, dest_path) -> dict[str, Any]  # PGM -> PPM (color)
```

---

## Exceptions

```python
class PgmError(Exception): ...
class PgmInvalidMagicError(PgmError): ...    # magic != "P2"/"P5"
class PgmInvalidHeaderError(PgmError): ...  # malformed header
class PgmSizeError(PgmError): ...           # file too large or dimensions unreasonable
class PgmDecodeError(PgmError): ...         # pixel data decode failure
```

---

## Security

- File size guard enforced: raises `PgmSizeError` for files exceeding safe limits
- Pure binary/text pixel data only; no XML or external resource loading
- Strict magic-byte validation before any decode attempt

---

## Quickstart

```python
import pgm

# Parse and inspect
img = pgm.parse_pgm_strict("samples/by-format/pgm/valid/2x2-gradient.pgm")
print(img.width, img.height, img.maxval, img.magic)

# Pixel stats
print(pgm.average_gray("samples/by-format/pgm/valid/2x2-gradient.pgm"))
print(pgm.min_max_gray("samples/by-format/pgm/valid/2x2-gradient.pgm"))

# Write
pgm.write_pgm([[0, 128], [64, 255]], 2, 2, 255, "/tmp/out.pgm")
```
