# ZST .NET Decompression Solution Design
# TC-RECON-W1-004 | PROB-001 | Corrected Technical Specification
# Reconciliation Finding REC-H-001

## Problem Statement

`ZstParser.cs` line 21 explicitly states:
> "Does NOT decompress — probe-only for metadata extraction"

`ZstDocument` has no `Decompress()` method and no `DecompressedContent` property.
A `.zst` format product that cannot decompress its own files is a documentation stub, not a library.

## Invalid Proposed Fix (phase-A investigation — REJECTED)

The original phase-A report proposed:
```
System.IO.Compression.GZipStream
```

**This is technically invalid.** `GZipStream` implements RFC 1952 (GZIP format, magic bytes `1F 8B`).
Zstandard uses RFC 8878 (magic bytes `28 B5 2F FD`). These are incompatible wire formats.
Attempting to decompress a `.zst` file with `GZipStream` will throw `InvalidDataException` on the first byte.

## Correct Solution: ZstdSharp.Port

**NuGet package:** `ZstdSharp.Port`
**License:** MIT (compatible with Format Factory commercial licensing)
**Type:** Pure managed .NET — no native DLLs, no P/Invoke, works on all .NET 6+ platforms (Windows, Linux, macOS, ARM)
**Author:** oleg-st
**Source:** https://github.com/oleg-st/ZstdSharp (MIT)

### Why ZstdSharp.Port

| Criterion | ZstdSharp.Port | ZstdNet | System.IO.Compression.ZstdStream (.NET 9) |
|-----------|---------------|---------|------------------------------------------|
| License | MIT | MIT | MIT |
| Pure managed | YES | NO (P/Invoke to libzstd native) | YES (.NET 9+ only) |
| .NET 6 support | YES | YES | NO (.NET 9+) |
| NuGet stable | YES | YES | N/A (runtime built-in) |
| Cross-platform | YES | Partial (requires libzstd.so) | YES |
| Streaming API | YES | YES | YES |
| Block API | YES | YES | NO |

### API Usage

```csharp
// Add to FormatFactory.Zst.csproj:
// <PackageReference Include="ZstdSharp.Port" Version="0.8.*" />

using ZstdSharp;

// Option A: Full decompression (small files)
public static byte[] Decompress(byte[] compressedData)
{
    using var decompressor = new Decompressor();
    return decompressor.Unwrap(compressedData).ToArray();
}

// Option B: Streaming decompression (large files)
public static Stream OpenDecompressionStream(Stream compressedStream)
{
    return new DecompressionStream(compressedStream);
}
```

### Changes Required to PROB-001

1. **`FormatFactory.Zst.csproj`** — add `<PackageReference Include="ZstdSharp.Port" Version="0.8.*" />`
2. **`ZstDocument.cs`** — add `DecompressedContent` property OR `Decompress()` instance method
3. **`ZstParser.cs`** — add `Decompress(string filePath)` and `DecompressStream(Stream compressed)` static methods
4. **`ZstParser.cs` line 21 comment** — update to reflect decompression capability
5. **`ZstParser.cs` line 5 header** — update Gate 11 status once commercial readiness is confirmed
6. **Tests** — add `tests/net/zst/ZstR117DecompressionTests.cs` with round-trip verify

### Sequencing (per PROB-001 classification HARDEN_BEFORE_EXECUTION)

```
PROB-009 GAP TAXONOMY REPAIR  -->  GAP entry for ZST decompression gets correct category
TC-HARD-H-001 ZstdSharp design -->  (this document)
TC-RECON-W4-001 execution     -->  add ZstdSharp.Port, implement Decompress(), add tests
```

PROB-001 is blocked by PROB-009 because without gap taxonomy repair, a gap entry for
"ZST decompression missing" cannot be created with a meaningful category — it would become
entry #1210 with category='MISSING', contributing to the taxonomy problem.

### Security Posture Preserved

The existing security posture (`MaxFileSizeBytes = 256 MB`, magic byte validation) must be
retained. Add a decompressed-size guard:
```csharp
public const long DefaultMaxDecompressedSizeBytes = 1L * 1024 * 1024 * 1024; // 1 GB
```
This prevents zip-bomb-style attacks on decompression.

### Verification

```bash
dotnet add src/net/zst/FormatFactory.Zst.csproj package ZstdSharp.Port
dotnet build src/net/zst/ --configuration Release
dotnet test tests/net/zst/ --configuration Release
```

Expected: `ZstR117DecompressionTests` all pass; `ZstR117DocumentPropertiesTests` still pass.

## Status

- Corrected fix: ZstdSharp.Port (MIT, pure managed)
- Rejected fix: System.IO.Compression.GZipStream (wrong RFC)
- Classification: HARDEN_BEFORE_EXECUTION (blocked by PROB-009 gap taxonomy first)
- Taskcard: TC-RECON-W4-001 (Wave 4 — after Wave 2 gap taxonomy repair)
