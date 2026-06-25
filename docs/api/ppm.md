# PPM Python API Reference

**Package:** `aspose-format-factory-ppm`
**Version:** 0.1.0
**Format:** Portable Pixmap (PPM) — Netpbm P3/P6
**Spec:** Netpbm specification (24-bit RGB color raster)

---

## Installation

```bash
pip install aspose-format-factory-ppm
```

```python
import ppm
```

---

## Core Functions

### `parse_ppm_strict`

```python
def parse_ppm_strict(file_path: str | Path) -> PpmImage
```

Parse a PPM file (P3 ASCII or P6 binary) and return a `PpmImage` object.
Raises `PpmInvalidMagicError`, `PpmInvalidHeaderError`, `PpmSizeError`, or `PpmDecodeError` on failure.

### `parse_ppm`

```python
def parse_ppm(file_path: str | Path) -> dict[str, Any]
```

Parse a PPM file and return a dictionary with keys: `magic`, `width`, `height`, `maxval`, `pixels`.
Each pixel in `pixels` is a `(R, G, B)` tuple.

### `probe_ppm`

```python
def probe_ppm(file_path: str | Path) -> dict[str, Any]
```

Probe a PPM file for header metadata without decoding pixel data.
Returns `magic`, `width`, `height`, `maxval`, `file_size`.

### `write_ppm`

```python
def write_ppm(pixels: list[list[tuple[int, int, int]]], width: int, height: int, maxval: int, dest_path: str | Path, *, binary: bool = True) -> dict[str, Any]
```

Write RGB pixel data to a PPM file. `pixels` is a list of rows; each element is `(R, G, B)` with values 0–`maxval`.
Set `binary=False` for P3 (ASCII) output.

---

## Domain Model

### `PpmImage`

```python
@dataclass
class PpmImage:
    spec_qname: ClassVar[str] = "ppm:image"
    path: Path
    magic: str                          # "P3" or "P6"
    width: int
    height: int
    maxval: int                         # max channel value (typically 255)
    pixels: list[list[tuple[int,int,int]]]  # row-major (R,G,B) tuples
```

---

## Pixel Analytics

### Dimensions

```python
def get_dimensions(file_path) -> tuple[int, int]    # (width, height)
def pixel_count(file_path) -> int
def ppm_pixel_count(file_path) -> int
def ppm_row_count(file_path) -> int
def ppm_column_count(file_path) -> int
def ppm_megapixels(file_path) -> float
def ppm_aspect_ratio(file_path) -> float
def ppm_dimension_ratio(file_path) -> float
def ppm_min_dimension(file_path) -> int
def ppm_max_dimension(file_path) -> int
def ppm_perimeter(file_path) -> int
```

### Color Channel Analytics

```python
def average_color(file_path) -> tuple[float, float, float]   # (R, G, B) averages
def ppm_red_channel_average(file_path) -> float
def ppm_green_channel_average(file_path) -> float
def ppm_blue_channel_average(file_path) -> float
def ppm_red_channel_sum(file_path) -> int
def ppm_green_channel_sum(file_path) -> int
def ppm_blue_channel_sum(file_path) -> int
def ppm_channel_range(file_path) -> dict[str, int]     # {"red": int, "green": int, "blue": int}
def ppm_channel_balance(file_path) -> float            # max_avg / (sum_avg + 1)
def ppm_dominant_channel(file_path) -> str             # "red", "green", or "blue"
def ppm_max_channel_sum(file_path) -> int
def ppm_min_channel_sum(file_path) -> int
```

### Brightness Statistics

```python
def ppm_luminance_average(file_path) -> float          # 0.299R + 0.587G + 0.114B
def ppm_brightness_variance(file_path) -> float
def ppm_min_max_brightness(file_path) -> dict[str, float]   # {"min": float, "max": float}
def ppm_saturation_estimate(file_path) -> float
```

### Color Properties

```python
def ppm_unique_color_count(file_path) -> int
def ppm_is_grayscale(file_path) -> bool                # R==G==B for all pixels
def is_grayscale(file_path) -> bool
def ppm_is_binary(file_path) -> bool                   # only 2 distinct pixel values
def ppm_has_pure_black(file_path) -> bool              # has (0,0,0) pixel
def ppm_has_pure_white(file_path) -> bool              # has (maxval,maxval,maxval) pixel
def ppm_is_dark(file_path) -> bool                     # avg luminance < 128
```

### Shape Properties

```python
def ppm_is_square(file_path) -> bool
def ppm_is_landscape(file_path) -> bool
def ppm_is_tall(file_path) -> bool
def ppm_is_portrait(file_path) -> bool
def ppm_pixel_density(file_path) -> float
```

---

## Transform Operations

```python
def flip_horizontal(file_path, dest_path) -> dict[str, Any]
def flip_vertical(file_path, dest_path) -> dict[str, Any]
def rotate_90(file_path, dest_path) -> dict[str, Any]
def invert(file_path, dest_path) -> dict[str, Any]        # invert all channels
def crop(file_path, dest_path, x, y, w, h) -> dict[str, Any]
def brightness(file_path, dest_path, factor: float) -> dict[str, Any]
def to_grayscale(file_path, dest_path) -> dict[str, Any]  # PPM -> PGM
```

---

## Conversion

```python
# ppm.ppm_to_pgm module
def convert_ppm_to_pgm(file_path, dest_path) -> dict[str, Any]  # PPM -> PGM (grayscale)
```

---

## Exceptions

```python
class PpmError(Exception): ...
class PpmInvalidMagicError(PpmError): ...    # magic != "P3"/"P6"
class PpmInvalidHeaderError(PpmError): ...  # malformed header
class PpmSizeError(PpmError): ...           # file too large or dimensions unreasonable
class PpmDecodeError(PpmError): ...         # pixel data decode failure
```

---

## Security

- File size guard enforced: raises `PpmSizeError` for files exceeding safe limits
- Pure binary/text pixel data only; no XML or external resource loading
- Strict magic-byte validation before any decode attempt

---

## Quickstart

```python
import ppm

# Parse and inspect
img = ppm.parse_ppm_strict("samples/by-format/ppm/valid/2x2-rgbw.ppm")
print(img.width, img.height, img.maxval, img.magic)

# Color analytics
print(ppm.average_color("samples/by-format/ppm/valid/2x2-rgbw.ppm"))
print(ppm.ppm_dominant_channel("samples/by-format/ppm/valid/2x2-rgbw.ppm"))

# Write
pixels = [[(255, 0, 0), (0, 255, 0)], [(0, 0, 255), (255, 255, 255)]]
ppm.write_ppm(pixels, 2, 2, 255, "/tmp/out.ppm")
```
