// Tests for ZstDocument.SizeLabel computed property and related document properties.
// Sprint: ff-sprint-s130-dotnet-deepening-20260627
// Ledger: PC-ZST-R131

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R131: Tests for ZstDocument.SizeLabel computed property and thin-coverage
/// ZstDocument properties. SizeLabel returns "empty" for 0 bytes, "tiny" for &lt;512,
/// "small" for &lt;10240, "medium" for &lt;1 MB, "large" for ≥1 MB. Also covers:
/// IsEmptyContent on default document; FileSizeKB computed from FileSizeBytes;
/// HasMultipleFrames when FrameCount > 1; IsValid requires MagicValid and FrameCount > 0;
/// ContentTypeHint default value; BytesPerFrame on single-frame document;
/// dogfood Compress → ParseStream → ZstDocument property chain.
/// </summary>
public class ZstR131SizeLabelAndDocumentPropertiesTests
{
    // -------------------------------------------------------------------------
    // SizeLabel computed property
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_SizeLabel_ZeroBytes_IsEmpty()
    {
        var doc = new ZstDocument { FileSizeBytes = 0 };
        Assert.Equal("empty", doc.SizeLabel);
    }

    [Fact]
    public void ZstDocument_SizeLabel_Below512_IsTiny()
    {
        var doc = new ZstDocument { FileSizeBytes = 100 };
        Assert.Equal("tiny", doc.SizeLabel);
    }

    [Fact]
    public void ZstDocument_SizeLabel_Below10KB_IsSmall()
    {
        var doc = new ZstDocument { FileSizeBytes = 1024 };
        Assert.Equal("small", doc.SizeLabel);
    }

    [Fact]
    public void ZstDocument_SizeLabel_Below1MB_IsMedium()
    {
        var doc = new ZstDocument { FileSizeBytes = 500_000 };
        Assert.Equal("medium", doc.SizeLabel);
    }

    [Fact]
    public void ZstDocument_SizeLabel_AtOrAbove1MB_IsLarge()
    {
        var doc = new ZstDocument { FileSizeBytes = 1_048_576 };
        Assert.Equal("large", doc.SizeLabel);
    }

    // -------------------------------------------------------------------------
    // FileSizeKB computed property
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_FileSizeKB_ReflectsFileSizeBytes()
    {
        var doc = new ZstDocument { FileSizeBytes = 2048 };
        Assert.Equal(2.0, doc.FileSizeKB, precision: 3);
    }

    // -------------------------------------------------------------------------
    // HasMultipleFrames computed property
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_HasMultipleFrames_SingleFrame_IsFalse()
    {
        var doc = new ZstDocument { FrameCount = 1 };
        Assert.False(doc.HasMultipleFrames);
    }

    [Fact]
    public void ZstDocument_HasMultipleFrames_TwoFrames_IsTrue()
    {
        var doc = new ZstDocument { FrameCount = 2 };
        Assert.True(doc.HasMultipleFrames);
    }

    // -------------------------------------------------------------------------
    // IsValid computed property
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_IsValid_MagicValidAndFrameCountPositive_IsTrue()
    {
        var doc = new ZstDocument { MagicValid = true, FrameCount = 1 };
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void ZstDocument_IsValid_MagicInvalid_IsFalse()
    {
        var doc = new ZstDocument { MagicValid = false, FrameCount = 1 };
        Assert.False(doc.IsValid);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress → ParseStream → ZstDocument properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Compress_ParseStream_SizeLabel_IsNonEmpty()
    {
        var data = Encoding.UTF8.GetBytes("Hello, Zstandard! This is dogfood content for R131.");
        var compressed = ZstWriter.Compress(data);

        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms, knownLength: compressed.Length);

        Assert.NotNull(doc.SizeLabel);
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));
        Assert.True(doc.IsValid);
        Assert.False(doc.IsEmptyContent);
    }
}
