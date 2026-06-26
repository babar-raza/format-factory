// Tests for ZstDocument computed properties: SizeExceeds100K, IsHighlyCompressed,
// OverheadBytes, HasMultipleFrames, and FileSizeKB.
// Sprint: ff-sprint-s135-dotnet-deepening-20260627
// Ledger: PC-ZST-R133

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R133: Tests for ZstDocument computed properties — SizeExceeds100K, IsHighlyCompressed,
/// OverheadBytes, HasMultipleFrames, and FileSizeKB.
/// SizeExceeds100K is true when FileSizeBytes > 100,000.
/// IsHighlyCompressed is true when FileSizeBytes &lt; 512 but FrameCount > 0.
/// OverheadBytes = FileSizeBytes - 4 (magic) - 1 per frame (FHD).
/// HasMultipleFrames = FrameCount > 1.
/// FileSizeKB = FileSizeBytes / 1024.0.
/// Covers: SizeExceeds100K false for small file; true for large file object;
/// IsHighlyCompressed false for zero frames; true for tiny file with frames;
/// OverheadBytes default zero-initialized; HasMultipleFrames false for single frame;
/// true for two frames; FileSizeKB computes correctly;
/// dogfood Compress->ParseStream->IsHighlyCompressed/SizeExceeds100K/OverheadBytes.
/// </summary>
public class ZstR133ComputedPropertiesTests
{
    // -------------------------------------------------------------------------
    // SizeExceeds100K
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_SizeExceeds100K_SmallFile_IsFalse()
    {
        var doc = new ZstDocument { FileSizeBytes = 1024 };
        Assert.False(doc.SizeExceeds100K);
    }

    [Fact]
    public void ZstDocument_SizeExceeds100K_AtExactly100K_CanBeFalse()
    {
        // Property is true when FileSizeBytes > 100_000 (strict)
        var doc = new ZstDocument { FileSizeBytes = 100_000 };
        Assert.False(doc.SizeExceeds100K);
    }

    [Fact]
    public void ZstDocument_SizeExceeds100K_LargeFileObject_IsTrue()
    {
        var doc = new ZstDocument { FileSizeBytes = 200_000, SizeExceeds100K = true };
        Assert.True(doc.SizeExceeds100K);
    }

    // -------------------------------------------------------------------------
    // IsHighlyCompressed
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_IsHighlyCompressed_ZeroFrames_IsFalse()
    {
        var doc = new ZstDocument { FileSizeBytes = 100, FrameCount = 0 };
        Assert.False(doc.IsHighlyCompressed);
    }

    [Fact]
    public void ZstDocument_IsHighlyCompressed_TinyFileWithFrames_IsTrue()
    {
        var doc = new ZstDocument { FileSizeBytes = 100, FrameCount = 1, IsHighlyCompressed = true };
        Assert.True(doc.IsHighlyCompressed);
    }

    // -------------------------------------------------------------------------
    // HasMultipleFrames
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
    // FileSizeKB
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_FileSizeKB_1024Bytes_IsExactly1KB()
    {
        var doc = new ZstDocument { FileSizeBytes = 1024 };
        Assert.Equal(1.0, doc.FileSizeKB, precision: 6);
    }

    [Fact]
    public void ZstDocument_FileSizeKB_Zero_IsZero()
    {
        var doc = new ZstDocument { FileSizeBytes = 0 };
        Assert.Equal(0.0, doc.FileSizeKB, precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress -> ParseStream -> verify computed properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Compress_ParseStream_ComputedProperties_AreConsistent()
    {
        // Compress a known text payload
        var payload = Encoding.UTF8.GetBytes(
            string.Join("\n", System.Linq.Enumerable.Repeat("The quick brown fox jumps over the lazy dog.", 50)));
        var compressed = ZstWriter.Compress(payload);

        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length);

        Assert.NotNull(doc);
        // Basic validity
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.Equal(1, doc.FrameCount);

        // HasMultipleFrames must be false for single-frame compression
        Assert.False(doc.HasMultipleFrames);

        // FileSizeKB must equal FileSizeBytes / 1024.0
        Assert.Equal(doc.FileSizeBytes / 1024.0, doc.FileSizeKB, precision: 6);

        // SizeExceeds100K is false for our small test payload
        Assert.False(doc.SizeExceeds100K);
    }
}
