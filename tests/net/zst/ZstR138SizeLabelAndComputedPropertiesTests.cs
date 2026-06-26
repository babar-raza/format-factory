// Tests for ZstDocument.SizeLabel, IsEmptyContent, FileSizeKB, HasMultipleFrames, IsValid.
// Sprint: ff-sprint-s146-dotnet-deepening-20260628
// Ledger: PC-ZST-R138

using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R138: Dedicated tests for ZstDocument computed properties:
/// SizeLabel, IsEmptyContent, FileSizeKB, HasMultipleFrames, IsValid, ContentTypeHint.
/// SizeLabel: "empty" (0 bytes), "tiny" (&lt;512), "small" (&lt;10KB), "medium" (&lt;1MB), "large" (>=1MB).
/// IsEmptyContent: true if FileSizeBytes==0 after skipping magic bytes.
/// FileSizeKB: FileSizeBytes / 1024.0. HasMultipleFrames: FrameCount > 1.
/// IsValid: MagicValid && FrameCount > 0. ContentTypeHint: default "unknown".
/// Covers: SizeLabel default="empty"; FileSizeKB default=0.0; HasMultipleFrames=false when FrameCount=1;
/// IsValid=false when default ZstDocument; ContentTypeHint default="unknown";
/// IsEmptyContent default=true; SizeLabel "tiny" for small data; SizeLabel "small" for medium data;
/// dogfood compress->parse->SizeLabel not empty; dogfood compress->parse->IsValid=true.
/// </summary>
public class ZstR138SizeLabelAndComputedPropertiesTests
{
    // -------------------------------------------------------------------------
    // Default ZstDocument property tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_SizeLabel_Default_IsEmpty()
    {
        Assert.Equal("empty", new ZstDocument().SizeLabel);
    }

    [Fact]
    public void ZstDocument_FileSizeKB_Default_IsZero()
    {
        Assert.Equal(0.0, new ZstDocument().FileSizeKB);
    }

    [Fact]
    public void ZstDocument_HasMultipleFrames_Default_IsFalse()
    {
        Assert.False(new ZstDocument().HasMultipleFrames);
    }

    [Fact]
    public void ZstDocument_IsValid_Default_IsFalse()
    {
        // Default ZstDocument: MagicValid=false, FrameCount=0 → IsValid=false
        Assert.False(new ZstDocument().IsValid);
    }

    [Fact]
    public void ZstDocument_ContentTypeHint_Default_IsUnknown()
    {
        Assert.Equal("unknown", new ZstDocument().ContentTypeHint);
    }

    [Fact]
    public void ZstDocument_IsEmptyContent_Default_IsTrue()
    {
        // Default ZstDocument: FileSizeBytes=0 → IsEmptyContent=true
        Assert.True(new ZstDocument().IsEmptyContent);
    }

    // -------------------------------------------------------------------------
    // SizeLabel boundary tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_SizeLabel_TinyRange_ReturnsTiny()
    {
        // Create a doc with FileSizeBytes in [1, 511]
        var doc = new ZstDocument { FileSizeBytes = 100 };
        Assert.Equal("tiny", doc.SizeLabel);
    }

    [Fact]
    public void ZstDocument_SizeLabel_SmallRange_ReturnsSmall()
    {
        // FileSizeBytes in [512, 10239]
        var doc = new ZstDocument { FileSizeBytes = 1024 };
        Assert.Equal("small", doc.SizeLabel);
    }

    // -------------------------------------------------------------------------
    // Dogfood: compress->parse->properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CompressParse_SizeLabel_NotEmpty()
    {
        var data = Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("ZstR138 test payload. ", 100)));
        var compressed = ZstWriter.Compress(data);
        using var stream = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length);
        Assert.NotEqual("empty", doc.SizeLabel);
    }

    [Fact]
    public void DogfoodPipeline_CompressParse_IsValid_IsTrue()
    {
        var data = Encoding.UTF8.GetBytes("Format Factory ZST computed properties test.");
        var compressed = ZstWriter.Compress(data);
        using var stream = new System.IO.MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length);
        Assert.True(doc.IsValid);
    }
}
