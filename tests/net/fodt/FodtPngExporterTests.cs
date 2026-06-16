// FormatFactory.Fodt Tests -- FodtPngExporter Prototype Tests
// Sprint: product-deepening-fodt-png-export-20260616
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for the FODT → PNG document-outline thumbnail exporter.
///
/// Covers:
///   - ExportToPngBytes returns non-empty array
///   - PNG signature (first 8 bytes)
///   - IHDR chunk present at offset 8
///   - IEND marker at tail
///   - IDAT chunk present
///   - Empty document produces 1×1 minimal PNG
///   - Non-empty document produces larger PNG
///   - IHDR dimensions match expected paragraph layout
///   - Result metadata (WidthPx, HeightPx, ParagraphsRendered)
///   - Export from file path creates file
///   - Null argument guards
/// </summary>
public class FodtPngExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private static readonly string HeadingsFodt =
        Path.Combine(FixturesDir, "fodt-headings-and-list.fodt");

    private readonly string _tempDir;

    public FodtPngExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), $"fodt-png-{Guid.NewGuid():N}");
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
        var doc = FodtDocument.CreateEmpty();
        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        Assert.NotNull(bytes);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void ExportToPngBytes_EmptyDoc_HasPngSignature()
    {
        var doc = FodtDocument.CreateEmpty();
        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

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
        var doc = FodtDocument.CreateEmpty();
        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        Assert.True(bytes.Length >= 16);
        Assert.Equal((byte)'I', bytes[12]);
        Assert.Equal((byte)'H', bytes[13]);
        Assert.Equal((byte)'D', bytes[14]);
        Assert.Equal((byte)'R', bytes[15]);
    }

    [Fact]
    public void ExportToPngBytes_EmptyDoc_HasIendChunk()
    {
        var doc = FodtDocument.CreateEmpty();
        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        int iendOffset = bytes.Length - 8;
        Assert.Equal((byte)'I', bytes[iendOffset]);
        Assert.Equal((byte)'E', bytes[iendOffset + 1]);
        Assert.Equal((byte)'N', bytes[iendOffset + 2]);
        Assert.Equal((byte)'D', bytes[iendOffset + 3]);
    }

    [Fact]
    public void ExportToPngBytes_EmptyDoc_HasIdatChunk()
    {
        var doc = FodtDocument.CreateEmpty();
        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        bool found = false;
        for (int i = 0; i < bytes.Length - 4; i++)
        {
            if (bytes[i] == 'I' && bytes[i+1] == 'D' && bytes[i+2] == 'A' && bytes[i+3] == 'T')
            {
                found = true;
                break;
            }
        }
        Assert.True(found, "PNG must contain IDAT chunk");
    }

    // -------------------------------------------------------------------------
    // IHDR dimensions
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPngBytes_EmptyDoc_IhdrIs1x1()
    {
        var doc = FodtDocument.CreateEmpty();
        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        int width = (bytes[16] << 24) | (bytes[17] << 16) | (bytes[18] << 8) | bytes[19];
        int height = (bytes[20] << 24) | (bytes[21] << 16) | (bytes[22] << 8) | bytes[23];

        Assert.Equal(1, width);
        Assert.Equal(1, height);
    }

    [Fact]
    public void ExportToPngBytes_OneParagraph_IhdrWidthIs200()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world");

        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        int width = (bytes[16] << 24) | (bytes[17] << 16) | (bytes[18] << 8) | bytes[19];
        Assert.Equal(200, width);
    }

    [Fact]
    public void ExportToPngBytes_OneParagraph_IhdrHeightIs5()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");

        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        // 1 paragraph * (4 bar + 1 gap) = 5 px height
        int height = (bytes[20] << 24) | (bytes[21] << 16) | (bytes[22] << 8) | bytes[23];
        Assert.Equal(5, height);
    }

    [Fact]
    public void ExportToPngBytes_ThreeParagraphs_IhdrHeightIs15()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        doc.AppendParagraph("Second paragraph");
        doc.AppendParagraph("Third paragraph");

        byte[] bytes = FodtPngExporter.ExportToPngBytes(doc);

        // 3 paragraphs * 5 = 15
        int height = (bytes[20] << 24) | (bytes[21] << 16) | (bytes[22] << 8) | bytes[23];
        Assert.Equal(15, height);
    }

    // -------------------------------------------------------------------------
    // Result metadata
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_EmptyDoc_MetadataIsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        var pngPath = Path.Combine(_tempDir, "empty.png");
        var result = FodtPngExporter.ExportToPng(doc, pngPath);

        Assert.Equal(0, result.ParagraphsRendered);
        Assert.Equal(1, result.WidthPx);
        Assert.Equal(1, result.HeightPx);
    }

    [Fact]
    public void ExportToPng_TwoParagraphs_MetadataIsCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para one");
        doc.AppendParagraph("Para two");

        var pngPath = Path.Combine(_tempDir, "two.png");
        var result = FodtPngExporter.ExportToPng(doc, pngPath);

        Assert.Equal(2, result.ParagraphsRendered);
        Assert.Equal(200, result.WidthPx);
        Assert.Equal(10, result.HeightPx); // 2 * 5
    }

    // -------------------------------------------------------------------------
    // Export from file path
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_FromFilePath_CreatesNonEmptyFile()
    {
        var pngPath = Path.Combine(_tempDir, "fromfile.png");
        var result = FodtPngExporter.ExportToPng(MinimalFodt, pngPath);

        Assert.True(File.Exists(pngPath));
        Assert.True(new FileInfo(pngPath).Length > 0);
        Assert.Equal(pngPath, result.OutputPath);
    }

    [Fact]
    public void ExportToPng_FromFilePath_HasPngSignature()
    {
        var pngPath = Path.Combine(_tempDir, "sig.png");
        FodtPngExporter.ExportToPng(MinimalFodt, pngPath);

        byte[] bytes = File.ReadAllBytes(pngPath);
        Assert.Equal(0x89, bytes[0]);
        Assert.Equal((byte)'P', bytes[1]);
        Assert.Equal((byte)'N', bytes[2]);
        Assert.Equal((byte)'G', bytes[3]);
    }

    // -------------------------------------------------------------------------
    // Non-empty larger than empty
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPngBytes_DocumentWithParagraphs_LargerThanEmptyDoc()
    {
        var empty = FodtDocument.CreateEmpty();
        var filled = FodtDocument.CreateEmpty();
        filled.AppendParagraph("Some paragraph text here");
        filled.AppendParagraph("Another paragraph with more text");

        byte[] emptyBytes = FodtPngExporter.ExportToPngBytes(empty);
        byte[] filledBytes = FodtPngExporter.ExportToPngBytes(filled);

        Assert.True(filledBytes.Length > emptyBytes.Length,
            $"Filled PNG ({filledBytes.Length}) should be larger than empty ({emptyBytes.Length})");
    }

    // -------------------------------------------------------------------------
    // Null argument guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPng_NullFilePath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPngExporter.ExportToPng((string)null!, Path.Combine(_tempDir, "x.png")));
    }

    [Fact]
    public void ExportToPng_NullOutputPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPngExporter.ExportToPng(MinimalFodt, null!));
    }

    [Fact]
    public void ExportToPng_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPngExporter.ExportToPng((FodtDocument)null!, Path.Combine(_tempDir, "x.png")));
    }

    [Fact]
    public void ExportToPngBytes_NullDocument_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            FodtPngExporter.ExportToPngBytes(null!));
    }
}
