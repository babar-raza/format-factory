# FormatFactory.Zst

Commercial .NET library for Zstandard compressed files (.zst). Parse, compress, decompress, and inspect ZST files (RFC 8878).

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:31+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Zst
```
<!-- END:README-INSTALLATION -->

## Quick Start

```csharp
using FormatFactory.Zst;

// Parse metadata from an existing .zst file
var doc = ZstParser.Parse("archive.zst");
Console.WriteLine($"Valid: {doc.IsValid}, Frames: {doc.FrameCount}, Size: {doc.SizeLabel}");

// Compress data
byte[] data = System.Text.Encoding.UTF8.GetBytes("Hello, Zstandard!");
byte[] compressed = ZstWriter.Compress(data, level: 3);

// Decompress
byte[] restored = ZstWriter.Decompress(compressed);

// Compress to file
ZstWriter.CompressToFile(data, "output.zst");
```

## Features

- Parse and inspect Zstandard frame headers (RFC 8878)
- Compress byte arrays and streams at levels 1–22
- Decompress byte arrays and streams
- Security: file size guard (256 MB), decompression output guard (512 MB)

## Gate Status

Gate 11 status: commercial_readiness_in_progress. Babar Raza approval required before commercial release.
See `product-capability-matrix/poc-targets.yaml` for capability matrix entry.

## License

Commercial — Format Factory product. See root LICENSE for terms.

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:31+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | Zstandard Compressed File |
| Track | dotnet |
| Package | FormatFactory.Zst |
| Version | 0.1.0-r85-poc |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | IETF RFC 8878 |
| QName coverage | 3/3 implemented |
| Source files | 4 |
| Test files | 168 |
<!-- END:README-PACKAGE_INFO -->
