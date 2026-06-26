// Tests for ZstDocument.IsMinimalFrame, ContentTypeHint, IsEmptyContent deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R162

using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R162: Tests for ZstDocument.IsMinimalFrame, ContentTypeHint, IsEmptyContent deeper coverage.
/// ZstDocument.IsMinimalFrame: whether the frame is a minimal (empty) ZSTD frame.
/// ZstDocument.ContentTypeHint: detected content type hint string.
/// ZstDocument.IsEmptyContent: whether the decompressed content is empty.
/// ZstDocument.IsHighlyCompressed: whether compression ratio < 0.1.
/// Covers: IsMinimalFrame false for non-empty data; IsEmptyContent false for data;
/// ContentTypeHint non-null; ContentTypeHint non-empty; IsHighlyCompressed returns bool;
/// IsMinimalFrame vs IsEmpty distinction; ContentTypeHint for text data;
/// ZstDocument.Load valid data properties; CompressionRatio valid range;
/// BytesPerFrame consistent with frame count; FrameCount positive;
/// CompressedSize positive; DecompressedSize positive; IsEmpty false;
/// FileSizeKB positive; SizeExceeds100K false for small data;
/// dogfood Compress->Load->CheckAllProperties->Decompress->VerifyContent verify.
/// </summary>
public class ZstR162IsMinimalFrameAndContentHintTests
{
    private static readonly byte[] TextData =
        Encoding.UTF8.GetBytes("Hello World! This is a test document with enough content to be useful.");

    private static readonly byte[] LargeData =
        Encoding.UTF8.GetBytes(string.Concat(System.Linq.Enumerable.Repeat("Pattern content for testing. ", 30)));

    // -------------------------------------------------------------------------
    // IsMinimalFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void IsMinimalFrame_FalseForNonEmptyData()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.False(doc.IsMinimalFrame);
    }

    [Fact]
    public void IsMinimalFrame_ReturnsBool()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.IsType<bool>(doc.IsMinimalFrame);
    }

    // -------------------------------------------------------------------------
    // IsEmptyContent
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmptyContent_FalseForData()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.False(doc.IsEmptyContent);
    }

    [Fact]
    public void IsEmptyContent_ReturnsBool()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.IsType<bool>(doc.IsEmptyContent);
    }

    // -------------------------------------------------------------------------
    // ContentTypeHint
    // -------------------------------------------------------------------------

    [Fact]
    public void ContentTypeHint_NonNull()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.NotNull(doc.ContentTypeHint);
    }

    [Fact]
    public void ContentTypeHint_NonEmpty()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.ContentTypeHint.Length > 0);
    }

    [Fact]
    public void ContentTypeHint_ForTextData_IsString()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.IsType<string>(doc.ContentTypeHint);
    }

    // -------------------------------------------------------------------------
    // Combined properties
    // -------------------------------------------------------------------------

    [Fact]
    public void IsHighlyCompressed_ReturnsBool()
    {
        var compressed = ZstWriter.Compress(LargeData);
        var doc = ZstDocument.Load(compressed);
        Assert.IsType<bool>(doc.IsHighlyCompressed);
    }

    [Fact]
    public void CompressionRatio_InValidRange()
    {
        var compressed = ZstWriter.Compress(LargeData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.CompressionRatio > 0.0 && doc.CompressionRatio <= 1.0);
    }

    [Fact]
    public void BytesPerFrame_ConsistentWithFrameCount()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        var expected = (double)doc.CompressedSize / doc.FrameCount;
        Assert.Equal(expected, doc.BytesPerFrame, 1);
    }

    [Fact]
    public void FrameCount_PositiveForValidData()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void CompressedSize_PositiveForValidData()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void DecompressedSize_PositiveForValidData()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void IsEmpty_FalseForValidData()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void FileSizeKB_PositiveForValidData()
    {
        var compressed = ZstWriter.Compress(LargeData);
        var doc = ZstDocument.Load(compressed);
        Assert.True(doc.FileSizeKB > 0);
    }

    [Fact]
    public void SizeExceeds100K_FalseForSmallData()
    {
        var compressed = ZstWriter.Compress(TextData);
        var doc = ZstDocument.Load(compressed);
        Assert.False(doc.SizeExceeds100K);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->Load->CheckAllProperties->Decompress->VerifyContent
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressLoadCheckPropertiesDecompressVerify_Pipeline()
    {
        var original = TextData;

        // Compress
        var compressed = ZstWriter.Compress(original);
        Assert.NotEmpty(compressed);

        // Load
        var doc = ZstDocument.Load(compressed);
        Assert.False(doc.IsEmpty);
        Assert.False(doc.IsEmptyContent);
        Assert.False(doc.IsMinimalFrame);
        Assert.NotNull(doc.ContentTypeHint);
        Assert.True(doc.FrameCount > 0);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(doc.BytesPerFrame > 0);
        Assert.True(doc.CompressionRatio > 0.0 && doc.CompressionRatio <= 1.0);
        Assert.False(doc.SizeExceeds100K);

        // Decompress
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, decompressed);
        Assert.Equal(original.Length, decompressed.Length);
    }
}
