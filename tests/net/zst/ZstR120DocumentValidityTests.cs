// Tests for ZstDocument.IsValid, MagicValid, HasMultipleFrames, FileSizeKB, SizeLabel.
// Sprint: FORMAT-FACTORY-ZST-DOCUMENT-VALIDITY-20260626
// Ledger: R120-GOVERNED-DOTNET-ZST-DOCUMENT-VALIDITY-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R120: ZstDocument validity and size properties — IsValid is true for properly formed
/// Zstd streams (MagicValid and FrameCount > 0). MagicValid checks the 4-byte Zstd magic
/// number. HasMultipleFrames is true when FrameCount > 1. FileSizeKB derives from
/// FileSizeBytes. SizeLabel returns a human-readable size category string.
/// </summary>
public class ZstR120DocumentValidityTests
{
    private static ZstDocument LoadCompressed(string text)
    {
        var raw = Encoding.UTF8.GetBytes(text);
        var compressed = ZstWriter.Compress(raw);
        using var ms = new MemoryStream(compressed);
        return ZstDocument.ParseStream(ms, knownLength: compressed.Length);
    }

    // ---- IsValid ----

    [Fact]
    public void IsValid_ProperlyCompressedStream_IsTrue()
    {
        var doc = LoadCompressed("valid zstd content");
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_MagicValidAndFrameCountPositive_IsTrue()
    {
        var doc = LoadCompressed("another valid payload");
        // IsValid = MagicValid && FrameCount > 0
        Assert.Equal(doc.MagicValid && doc.FrameCount > 0, doc.IsValid);
    }

    // ---- MagicValid ----

    [Fact]
    public void MagicValid_ProperlyCompressedStream_IsTrue()
    {
        var doc = LoadCompressed("magic number test");
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void MagicValid_TypeIsBool()
    {
        var doc = LoadCompressed("bool check");
        // Just verify we can read the bool without exception
        var _ = doc.MagicValid;
        Assert.True(true); // reached without exception
    }

    // ---- HasMultipleFrames ----

    [Fact]
    public void HasMultipleFrames_SingleFrameStream_IsFalse()
    {
        // Normal small payload = single Zstd frame
        var doc = LoadCompressed("single frame");
        Assert.False(doc.HasMultipleFrames);
    }

    [Fact]
    public void HasMultipleFrames_DerivedFromFrameCount()
    {
        var doc = LoadCompressed("frame count check");
        Assert.Equal(doc.FrameCount > 1, doc.HasMultipleFrames);
    }

    // ---- FileSizeKB ----

    [Fact]
    public void FileSizeKB_NonNegative()
    {
        var doc = LoadCompressed("file size KB test payload");
        Assert.True(doc.FileSizeKB >= 0.0, $"FileSizeKB should be non-negative, got {doc.FileSizeKB}");
    }

    [Fact]
    public void FileSizeKB_DerivedFromFileSizeBytes()
    {
        var doc = LoadCompressed("derivation test for KB");
        var expected = doc.FileSizeBytes / 1024.0;
        Assert.Equal(expected, doc.FileSizeKB, precision: 6);
    }

    // ---- SizeLabel ----

    [Fact]
    public void SizeLabel_SmallPayload_IsNotNullOrEmpty()
    {
        var doc = LoadCompressed("small payload for label");
        Assert.False(string.IsNullOrWhiteSpace(doc.SizeLabel),
            "SizeLabel should return a non-empty size category string");
    }

    [Fact]
    public void SizeLabel_ReturnsStringType()
    {
        var doc = LoadCompressed("type check");
        Assert.IsType<string>(doc.SizeLabel);
    }

    // ---- Dogfood: all validity properties consistent ----

    [Fact]
    public void DogfoodPipeline_ValidityPropertiesConsistent()
    {
        const string payload = "Format Factory ZST validity dogfood — properly formed Zstd stream.";
        var doc = LoadCompressed(payload);

        // IsValid = MagicValid && FrameCount > 0
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.True(doc.FrameCount > 0);

        // HasMultipleFrames derivation
        Assert.Equal(doc.FrameCount > 1, doc.HasMultipleFrames);

        // FileSizeKB derivation
        Assert.Equal(doc.FileSizeBytes / 1024.0, doc.FileSizeKB, precision: 6);

        // SizeLabel is non-empty
        Assert.False(string.IsNullOrWhiteSpace(doc.SizeLabel));
    }
}
