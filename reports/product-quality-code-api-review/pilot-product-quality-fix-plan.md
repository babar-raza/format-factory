# Pilot Product Quality Fix Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Pilot Objective

Execute one scoped, high-impact quality fix to prove the fix → verify → evidence loop works
before scaling to all 30 products in Phase F.

---

## Selected Pilot: ZST .NET Writer (PQ-007)

**Problem:** ZstDocument is a pure read-only DTO. No ZstWriter class exists. A compression
library with no ability to compress is not a usable product.

**Why ZST is the best pilot:**
1. CRITICAL severity, P0 priority — highest impact
2. Bounded scope — one new class, no changes to ZstParser or ZstDocument
3. Clear verification: roundtrip test (compress → decompress → compare)
4. Python ZST already has compress/decompress — the .NET product is the gap
5. No public API surface breaks — additive only (new class)

---

## Pilot Fix Specification

### New File: `src/net/zst/ZstWriter.cs`

```csharp
namespace FormatFactory.Zst
{
    /// <summary>
    /// Provides Zstandard (ZST) compression and decompression operations.
    /// </summary>
    public static class ZstWriter
    {
        /// <summary>
        /// Compresses a byte array using Zstandard compression.
        /// </summary>
        /// <param name="data">The data to compress.</param>
        /// <param name="compressionLevel">Compression level (1–22). Default: 3.</param>
        /// <returns>Compressed byte array.</returns>
        public static byte[] Compress(byte[] data, int compressionLevel = 3);

        /// <summary>
        /// Compresses source stream data into destination stream.
        /// </summary>
        public static void Compress(Stream source, Stream destination, int compressionLevel = 3);

        /// <summary>
        /// Decompresses a ZST-compressed byte array.
        /// </summary>
        /// <param name="data">Compressed data.</param>
        /// <returns>Decompressed byte array.</returns>
        public static byte[] Decompress(byte[] data);

        /// <summary>
        /// Decompresses from source stream into destination stream.
        /// </summary>
        public static void Decompress(Stream source, Stream destination);
    }
}
```

**Dependencies:** ZstdNet NuGet package (or SharpZstd, or managed implementation)

**Note:** .NET 7+ includes built-in `System.IO.Compression.ZLibStream` for zlib but NOT for
Zstandard. A dedicated Zstandard NuGet package is required. Options:
- `ZstdNet` (MIT, native wrapper) — recommended
- `SharpZstd` (pure managed)
- `ZstdSharp` (pure managed, actively maintained)

**Recommended:** ZstdSharp — pure managed implementation, no native DLL required.

---

## Pilot Fix Steps

### Step 1: Read existing ZST .NET source

```
Read: src/net/zst/ZstDocument.cs
Read: src/net/zst/ZstParser.cs
Read: src/net/zst/FormatFactory.Zst.csproj
```

### Step 2: Add ZstdSharp dependency

Edit `FormatFactory.Zst.csproj`:
```xml
<PackageReference Include="ZstdSharp.Port" Version="0.7.4" />
```

### Step 3: Write ZstWriter.cs

Create `src/net/zst/ZstWriter.cs` implementing the specification above.

Using ZstdSharp:
```csharp
using ZstdSharp;

public static byte[] Compress(byte[] data, int compressionLevel = 3)
{
    using var compressor = new Compressor(compressionLevel);
    return compressor.Wrap(data).ToArray();
}

public static byte[] Decompress(byte[] data)
{
    using var decompressor = new Decompressor();
    return decompressor.Unwrap(data).ToArray();
}
```

### Step 4: Write regression test

Create `tests/net/zst/ZstWriterRoundtripTests.cs`:

```csharp
[TestClass]
public class ZstWriterRoundtripTests
{
    [TestMethod]
    public void Compress_ThenDecompress_ReturnsOriginalBytes()
    {
        var original = Encoding.UTF8.GetBytes("Hello, Zstandard compression!");
        var compressed = ZstWriter.Compress(original);
        var decompressed = ZstWriter.Decompress(compressed);
        CollectionAssert.AreEqual(original, decompressed);
    }

    [TestMethod]
    public void Compress_ProducesSmaller_ForRepetitiveData()
    {
        var data = Encoding.UTF8.GetBytes(new string('a', 10000));
        var compressed = ZstWriter.Compress(data);
        Assert.IsTrue(compressed.Length < data.Length);
    }

    [TestMethod]
    public void CompressStream_ThenDecompressStream_Roundtrip()
    {
        var original = Encoding.UTF8.GetBytes("Stream-based compression test.");
        using var sourceStream = new MemoryStream(original);
        using var compressedStream = new MemoryStream();
        ZstWriter.Compress(sourceStream, compressedStream);

        compressedStream.Seek(0, SeekOrigin.Begin);
        using var decompressedStream = new MemoryStream();
        ZstWriter.Decompress(compressedStream, decompressedStream);

        CollectionAssert.AreEqual(original, decompressedStream.ToArray());
    }

    [TestMethod]
    public void Compress_CompressionLevels_1Through22_Succeed()
    {
        var data = Encoding.UTF8.GetBytes("Test data for multiple compression levels.");
        foreach (int level in new[] {1, 3, 6, 9, 15, 22})
        {
            var compressed = ZstWriter.Compress(data, level);
            var decompressed = ZstWriter.Decompress(compressed);
            CollectionAssert.AreEqual(data, decompressed, $"Failed at level {level}");
        }
    }
}
```

### Step 5: Run tests

```bash
cd tests/net/zst
dotnet test --filter "ZstWriterRoundtripTests" -v
```

**Expected:** 4/4 tests pass.

### Step 6: Update problem status

In `product-quality-problem-schema.json`:
- Set PQ-007 status to RESOLVED
- Add evidence: `src/net/zst/ZstWriter.cs` + test file path + test pass count

### Step 7: Record evidence bundle

```
.local/evidences/product-quality-fixes/pq-007-zst-writer/
├── evidence-declaration.yaml
├── ZstWriter.cs (copy)
├── ZstWriterRoundtripTests.cs (copy)
└── test-output.txt
```

---

## Pilot Success Criteria

| Criterion | Required |
|-----------|----------|
| ZstWriter.cs created | YES |
| Compress/Decompress methods public | YES |
| Stream overloads present | YES |
| Roundtrip test passes | YES |
| No ZstParser regressions | YES (run existing ZST tests) |
| PQ-007 status = RESOLVED | YES |
| evidence bundle written | YES |

---

## Pilot Verification Command

```bash
dotnet test tests/net/zst/ -v
```

Expected output:
```
Passed: ZstWriterRoundtripTests.Compress_ThenDecompress_ReturnsOriginalBytes
Passed: ZstWriterRoundtripTests.Compress_ProducesSmaller_ForRepetitiveData
Passed: ZstWriterRoundtripTests.CompressStream_ThenDecompressStream_Roundtrip
Passed: ZstWriterRoundtripTests.Compress_CompressionLevels_1Through22_Succeed
Passed: (existing ZST parser tests)
```

---

## Alternative Pilot: Python pyproject.toml Enrichment (if ZST is deferred)

If ZST .NET writer is deferred to Phase F due to NuGet dependency approval requirements:

**Pilot target:** Enrich `pyproject.toml` for all 20 Python packages (PQ-004)

**Changes per package:**
```toml
[project]
authors = [{name = "Format Factory Team"}]
readme = "README.md"
keywords = ["file-format", "parser", "converter"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Libraries",
]

[project.urls]
Homepage = "https://github.com/format-factory/format-factory"
Repository = "https://github.com/format-factory/format-factory"
```

**Effort:** XS per package × 20 packages = S total
**Verification:** `pip install -e src/python/fods/ && pip show aspose-format-factory-fods`
**Risk:** ZERO (metadata only, no behavioral changes)
