// FormatFactory.Fods Tests -- FodsPngExporter Prototype Tests
// Sprint: product-deepening-fods-png-export-20260616
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for the FODS → PNG thumbnail exporter.
///
/// Covers:
///   - ExportToPngBytes returns non-empty array
///   - First 8 bytes are PNG signature
///   - IHDR chunk present (bytes 8-28)
///   - IEND marker present at tail
///   - Empty document produces valid minimal PNG
///   - Non-empty sheet produces larger PNG than 1×1 placeholder
///   - Width/height encoded in IHDR match expected layout
///   - Null argument guards
///   - Export from file path creates file
///   - Result metadata (WidthPx, HeightPx, RowsRendered, ColsRendered)
///   - PNG IDAT chunk present
///   - Multi-row sheet thumbnail is taller than single-row
///   - Data cells affect PNG size
/// </summary>
public class FodsPngExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsPngExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), $"fods-png-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        try { Directory.Delete(_tempDir, recursive: true); } catch { /* best-effort */ }
    }

    // -------------------------------------------------------------------------
    // PNG signature and structure
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPngBytes_EmptyDoc_ReturnsNonEmptyArray()
    {
        var doc = FodsDocument.CreateNew();
        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToPngBytes_EmptyDoc_HasPngSignature()
    {
        var doc = FodsDocument.CreateNew();
        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        // PNG signature: 89 50 4E 47 0D 0A 1A 0A
        Assert.Equal(0x89, bytes[0]);
        Assert.Equal(0x50, bytes[1]); // 'P'
        Assert.Equal(0x4E, bytes[2]); // 'N'
        Assert.Equal(0x47, bytes[3]); // 'G'
        Assert.Equal(0x0D, bytes[4]);
        Assert.Equal(0x0A, bytes[5]);
        Assert.Equal(0x1A, bytes[6]);
        Assert.Equal(0x0A, bytes[7]);
    }

    [Fact]
    public void ExportToPngBytes_EmptyDoc_HasIhdrChunk()
    {
        var doc = FodsDocument.CreateNew();
        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        // After 8-byte signature: 4-byte length + "IHDR" (4 bytes)
        Assert.True(bytes.Length >= 16, "PNG must be at least 16 bytes");
        // IHDR chunk type at offset 12
        Assert.Equal((byte)'I', bytes[12]);
        Assert.Equal((byte)'H', bytes[13]);
        Assert.Equal((byte)'D', bytes[14]);
        Assert.Equal((byte)'R', bytes[15]);
    }

    [Fact]
    public void ExportToPngBytes_EmptyDoc_HasIendChunk()
    {
        var doc = FodsDocument.CreateNew();
        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        // IEND chunk: last 12 bytes are length(0)=00000000 + "IEND" + CRC
        Assert.True(bytes.Length >= 12);
        int iendTypeOffset = bytes.Length - 8;
        Assert.Equal((byte)'I', bytes[iendTypeOffset]);
        Assert.Equal((byte)'E', bytes[iendTypeOffset + 1]);
        Assert.Equal((byte)'N', bytes[iendTypeOffset + 2]);
        Assert.Equal((byte)'D', bytes[iendTypeOffset + 3]);
    }

    [Fact]
    public void ExportToPngBytes_EmptyDoc_HasIdatChunk()
    {
        var doc = FodsDocument.CreateNew();
        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        // Search for "IDAT" marker in bytes
        bool foundIdat = false;
        for (int i = 0; i < bytes.Length - 4; i++)
        {
            if (bytes[i] == 'I' && bytes[i+1] == 'D' && bytes[i+2] == 'A' && bytes[i+3] == 'T')
            {
                foundIdat = true;
                break;
            }
        }
        Assert.True(foundIdat, "PNG must contain an IDAT chunk");
    }

    // -------------------------------------------------------------------------
    // IHDR dimensions
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPngBytes_EmptyDoc_IhdrIs1x1()
    {
        var doc = FodsDocument.CreateNew();
        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        // IHDR data starts at offset 16 (8 sig + 4 len + 4 type)
        // Width at IHDR[0..3], Height at IHDR[4..7] (big-endian)
        int width = (bytes[16] << 24) | (bytes[17] << 16) | (bytes[18] << 8) | bytes[19];
        int height = (bytes[20] << 24) | (bytes[21] << 16) | (bytes[22] << 8) | bytes[23];

        Assert.Equal(1, width);
        Assert.Equal(1, height);
    }

    [Fact]
    public void ExportToPngBytes_SingleCell_IhdrDimensionsAreCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("S");
        doc.InsertRowWithValues("S", 0, new[] { "X" });

        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        // 1 row, 1 col → (1 col * (16+1) + 1) × (1 row * (16+1) + 1) = 18×18
        int width = (bytes[16] << 24) | (bytes[17] << 16) | (bytes[18] << 8) | bytes[19];
        int height = (bytes[20] << 24) | (bytes[21] << 16) | (bytes[22] << 8) | bytes[23];

        Assert.Equal(18, width);  // 1 col * 17 + 1
        Assert.Equal(18, height); // 1 row * 17 + 1
    }

    [Fact]
    public void ExportToPngBytes_TwoRowThreeCol_IhdrDimensionsAreCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Grid");
        doc.InsertRowWithValues("Grid", 0, new[] { "A", "B", "C" });
        doc.InsertRowWithValues("Grid", 1, new[] { "D", "E", "F" });

        byte[] bytes = FodsPngExporter.ExportToPngBytes(doc);

        // 2 rows, 3 cols → (3*17+1) × (2*17+1) = 52×35
        int width = (bytes[16] << 24) | (bytes[17] << 16) | (bytes[18] << 8) | bytes[19];
        int height = (bytes[20] << 24) | (bytes[21] << 16) | (bytes[22] << 8) | bytes[23];

        Assert.Equal(52, width);
        Assert.Equal(35, height);
    }

    // -------------------------------------------------------------------------
    // Result metadata
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_SingleCell_MetadataIsCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Hello" });

        var pngPath = Path.Combine(_tempDir, "meta.png");
        var result = FodsPngExporter.ExportToPng(doc, pngPath);

        Assert.Equal(18, result.WidthPx);
        Assert.Equal(18, result.HeightPx);
        Assert.Equal(1, result.RowsRendered);
        Assert.Equal(1, result.ColsRendered);
    }

    [Fact]
    public void ExportToPng_EmptyDoc_MetadataIsZeroRows()
    {
        var doc = FodsDocument.CreateNew();
        var pngPath = Path.Combine(_tempDir, "empty.png");
        var result = FodsPngExporter.ExportToPng(doc, pngPath);

        Assert.Equal(0, result.RowsRendered);
        Assert.Equal(0, result.ColsRendered);
        Assert.Equal(1, result.WidthPx);
        Assert.Equal(1, result.HeightPx);
    }

    // -------------------------------------------------------------------------
    // Export from file path
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_FromFilePath_CreatesNonEmptyFile()
    {
        var pngPath = Path.Combine(_tempDir, "fromfile.png");
        var result = FodsPngExporter.ExportToPng(MinimalFods, pngPath);

        Assert.True(File.Exists(pngPath));
        Assert.True(new FileInfo(pngPath).Length > 0);
        Assert.Equal(pngPath, result.OutputPath);
    }

    [Fact]
    public void ExportToPng_FromFilePath_HasPngSignature()
    {
        var pngPath = Path.Combine(_tempDir, "sig.png");
        FodsPngExporter.ExportToPng(MinimalFods, pngPath);

        byte[] bytes = File.ReadAllBytes(pngPath);
        Assert.Equal(0x89, bytes[0]);
        Assert.Equal(0x50, bytes[1]);
        Assert.Equal(0x4E, bytes[2]);
        Assert.Equal(0x47, bytes[3]);
    }

    // -------------------------------------------------------------------------
    // Null argument guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_NullFilePath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPngExporter.ExportToPng((string)null!, Path.Combine(_tempDir, "x.png")));
    }

    [Fact]
    public void ExportToPng_NullOutputPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPngExporter.ExportToPng(MinimalFods, null!));
    }

    [Fact]
    public void ExportToPng_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPngExporter.ExportToPng((FodsDocument)null!, Path.Combine(_tempDir, "x.png")));
    }

    [Fact]
    public void ExportToPngBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodsPngExporter.ExportToPngBytes(null!));
    }

    // -------------------------------------------------------------------------
    // Non-empty is larger than empty
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPngBytes_NonEmptySheet_LargerThanEmptyDoc()
    {
        var empty = FodsDocument.CreateNew();
        var filled = FodsDocument.CreateNew();
        filled.AddSheet("S");
        filled.InsertRowWithValues("S", 0, new[] { "Data" });

        byte[] emptyBytes = FodsPngExporter.ExportToPngBytes(empty);
        byte[] filledBytes = FodsPngExporter.ExportToPngBytes(filled);

        // Filled image (18×18) should compress to more bytes than 1×1 empty placeholder
        Assert.True(filledBytes.Length > emptyBytes.Length,
            $"Filled PNG ({filledBytes.Length} bytes) should be larger than empty ({emptyBytes.Length} bytes)");
    }
}
