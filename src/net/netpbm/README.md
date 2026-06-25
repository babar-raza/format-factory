# FormatFactory.Netpbm

.NET commercial library for Portable Bitmap/Graymap/Pixmap (PBM/PGM/PPM/PNM) format support.

## Features

- Parse PBM (Portable Bitmap, black-and-white), PGM (Portable Graymap), and PPM (Portable Pixmap) files
- Both ASCII (P1/P2/P3) and binary (P4/P5/P6) variants
- Write PBM/PGM/PPM files in ASCII or binary encoding
- Image transforms: flip horizontal/vertical, rotate 90/180/270
- Filters: grayscale, brightness, contrast, threshold, edge detection
- Drawing primitives: fill, rectangle, circle, pixel
- Overlay: alpha compositing, blending
- Export and conversion between Netpbm sub-formats
- Security: 64 MB file size guard, 65536 dimension guard, 1B pixel count guard

## Installation

Available as a NuGet package. Target framework: net10.0.

## Quick Start

```csharp
using FormatFactory.Netpbm;

// Parse a PPM file
var image = NetpbmParser.Parse("photo.ppm");
Console.WriteLine($"Width: {image.Width}, Height: {image.Height}, Format: {image.Format}");

// Write a PGM file
NetpbmWriter.Write(image, "output.pgm", NetpbmEncoding.Binary);

// Apply a transform
var flipped = NetpbmExporter.FlipHorizontal(image);
```

## Gate Status

Gate 11 status: commercial_readiness_in_progress. Babar Raza approval required before commercial release.
See `product-capability-matrix/poc-targets.yaml` for capability matrix entry.

## License

Commercial — Format Factory product. See root LICENSE for terms.
