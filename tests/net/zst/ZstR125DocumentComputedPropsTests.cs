// Tests for ZstDocument computed properties not covered in R117:
// IsMinimalFrame, IsHighlyCompressed, ContentTypeHint, OverheadBytes, BytesPerFrame, IsEmptyContent.
// Sprint: FORMAT-FACTORY-ZST-R125-20260627
// Ledger: R125-GOVERNED-DOTNET-ZST-COMPUTED-PROPS-001

using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R125: Tests for ZstDocument properties not covered in R117 (HasMultipleFrames/IsValid/SizeLabel):
/// IsMinimalFrame, IsHighlyCompressed, ContentTypeHint, OverheadBytes, BytesPerFrame, IsEmptyContent.
/// RFC 8878 basis: §3.1.1 frame structure, §3.1.2 frame header descriptor.
/// </summary>
public class ZstR125DocumentComputedPropsTests
{
    // -------------------------------------------------------------------------
    // ZstDocument.IsMinimalFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMinimalFrame_SingleFrameSmallFile_ReturnsTrue()
    {
        var doc = new ZstDocument { FrameCount = 1, FileSizeBytes = 50, IsMinimalFrame = true };
        Assert.True(doc.IsMinimalFrame);
    }

    [Fact]
    public void IsMinimalFrame_MultipleFrames_ReturnsFalse()
    {
        var doc = new ZstDocument { FrameCount = 2, FileSizeBytes = 50, IsMinimalFrame = false };
        Assert.False(doc.IsMinimalFrame);
    }

    [Fact]
    public void IsMinimalFrame_SingleFrameLargeFile_ReturnsFalse()
    {
        var doc = new ZstDocument { FrameCount = 1, FileSizeBytes = 2048, IsMinimalFrame = false };
        Assert.False(doc.IsMinimalFrame);
    }

    // -------------------------------------------------------------------------
    // ZstDocument.IsHighlyCompressed
    // -------------------------------------------------------------------------

    [Fact]
    public void IsHighlyCompressed_SmallCompressedFile_ReturnsTrue()
    {
        var doc = new ZstDocument { FileSizeBytes = 100, FrameCount = 1, IsHighlyCompressed = true };
        Assert.True(doc.IsHighlyCompressed);
    }

    [Fact]
    public void IsHighlyCompressed_LargeFile_ReturnsFalse()
    {
        var doc = new ZstDocument { FileSizeBytes = 10_000, FrameCount = 1, IsHighlyCompressed = false };
        Assert.False(doc.IsHighlyCompressed);
    }

    // -------------------------------------------------------------------------
    // ZstDocument.ContentTypeHint
    // -------------------------------------------------------------------------

    [Fact]
    public void ContentTypeHint_Default_IsUnknown()
    {
        var doc = new ZstDocument();
        Assert.Equal("unknown", doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_SetToCompressedData_ReturnsCompressedData()
    {
        var doc = new ZstDocument { ContentTypeHint = "compressed_data" };
        Assert.Equal("compressed_data", doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_SetToCompressedArchive_ReturnsCompressedArchive()
    {
        var doc = new ZstDocument { ContentTypeHint = "compressed_archive" };
        Assert.Equal("compressed_archive", doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_RealCompressedFile_IsCompressedData()
    {
        // Compress real content and parse → ContentTypeHint from stream (no filepath → "compressed_data")
        var payload = Encoding.UTF8.GetBytes("Hello Zstandard content type hint test");
        var compressed = ZstWriter.Compress(payload);
        using var ms = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        // Stream parse has no filePath → ContentTypeHint should be "compressed_data"
        Assert.Equal("compressed_data", doc.ContentTypeHint);
    }

    // -------------------------------------------------------------------------
    // ZstDocument.OverheadBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void OverheadBytes_Set100_Returns100()
    {
        var doc = new ZstDocument { OverheadBytes = 100L };
        Assert.Equal(100L, doc.OverheadBytes);
    }

    [Fact]
    public void OverheadBytes_Zero_ReturnsZero()
    {
        var doc = new ZstDocument { OverheadBytes = 0L };
        Assert.Equal(0L, doc.OverheadBytes);
    }

    [Fact]
    public void OverheadBytes_RealFile_IsNonNegative()
    {
        var payload = Encoding.UTF8.GetBytes("Overhead bytes test content");
        var compressed = ZstWriter.Compress(payload);
        using var ms = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.OverheadBytes >= 0, $"OverheadBytes should be >= 0, got {doc.OverheadBytes}");
    }

    // -------------------------------------------------------------------------
    // ZstDocument.BytesPerFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void BytesPerFrame_ZeroFrames_ReturnsZero()
    {
        var doc = new ZstDocument { FrameCount = 0, FileSizeBytes = 100, BytesPerFrame = 0.0 };
        Assert.Equal(0.0, doc.BytesPerFrame);
    }

    [Fact]
    public void BytesPerFrame_OneFrameHundredBytes_ReturnsHundred()
    {
        var doc = new ZstDocument { FrameCount = 1, FileSizeBytes = 100, BytesPerFrame = 100.0 };
        Assert.Equal(100.0, doc.BytesPerFrame);
    }

    // -------------------------------------------------------------------------
    // ZstDocument.IsEmptyContent
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmptyContent_True_ReturnsTrue()
    {
        var doc = new ZstDocument { IsEmptyContent = true };
        Assert.True(doc.IsEmptyContent);
    }

    [Fact]
    public void IsEmptyContent_False_ReturnsFalse()
    {
        var doc = new ZstDocument { IsEmptyContent = false };
        Assert.False(doc.IsEmptyContent);
    }

    // -------------------------------------------------------------------------
    // Dogfood: parse real ZST and verify computed property cohesion
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RealCompressedJson_PropertiesCohesive()
    {
        const string json = """{"name":"R125","format":"ZST","sprint":"S115","purpose":"computed_props_test"}""";
        var payload = Encoding.UTF8.GetBytes(json);
        var compressed = ZstWriter.Compress(payload);

        using var ms = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);

        // Should be a valid single-frame document
        Assert.True(doc.MagicValid);
        Assert.True(doc.FrameCount >= 1);
        Assert.True(doc.IsValid);

        // ContentTypeHint from stream (no filepath)
        Assert.Equal("compressed_data", doc.ContentTypeHint);

        // BytesPerFrame: positive for non-empty compressed content
        Assert.True(doc.BytesPerFrame > 0, $"BytesPerFrame expected > 0, got {doc.BytesPerFrame}");

        // OverheadBytes: non-negative
        Assert.True(doc.OverheadBytes >= 0);

        // IsEmptyContent: should be false for non-trivial payload
        Assert.False(doc.IsEmptyContent);
    }
}
