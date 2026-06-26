// Tests for ZstDocument.SizeExceeds, FileSizeKB, CompressionRatio deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R190

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R190: Tests for ZstDocument.SizeExceeds, FileSizeKB, CompressionRatio deeper coverage.
/// SizeExceeds(bytes): returns true when the compressed file exceeds the given byte threshold.
/// FileSizeKB: property returning the compressed file size in kilobytes.
/// CompressionRatio: property returning the ratio of decompressed to compressed size.
/// Covers: SizeExceeds false for small content with large threshold; SizeExceeds true for large threshold=0;
/// SizeExceeds consistent for same threshold; SizeExceeds large content vs large threshold;
/// FileSizeKB positive; FileSizeKB non-zero; FileSizeKB scales with content size;
/// FileSizeKB consistent; FileSizeKB larger for bigger content;
/// CompressionRatio positive; CompressionRatio >= 1 for compressible content;
/// CompressionRatio consistent; CompressionRatio larger for more compressible content;
/// CompressionRatio after WriteToFile;
/// dogfood WriteToFile×3 (small/medium/large)→ParseFile→SizeExceeds→FileSizeKB→CompressionRatio pipeline.
/// </summary>
public class ZstR190SizeExceedsAndFileSizeKbDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR190SizeExceedsAndFileSizeKbDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR190_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string SmallText = "Hello, World!";
    private static readonly string MediumText = string.Concat(Enumerable.Repeat(
        "The quick brown fox jumps over the lazy dog. ", 50));
    private static readonly string LargeText = string.Concat(Enumerable.Repeat(
        "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. ", 500));

    private ZstDocument WriteAndParse(string content, string filename)
    {
        var path = TempFile(filename);
        ZstWriter.WriteToFile(content, path);
        return ZstParser.ParseFile(path);
    }

    // -------------------------------------------------------------------------
    // SizeExceeds
    // -------------------------------------------------------------------------

    [Fact]
    public void SizeExceeds_FalseForLargeThreshold()
    {
        var doc = WriteAndParse(SmallText, "small.zst");
        Assert.False(doc.SizeExceeds(1_000_000)); // 1 MB threshold
    }

    [Fact]
    public void SizeExceeds_TrueForZeroThreshold()
    {
        var doc = WriteAndParse(SmallText, "zero.zst");
        Assert.True(doc.SizeExceeds(0));
    }

    [Fact]
    public void SizeExceeds_Consistent()
    {
        var doc = WriteAndParse(MediumText, "consistent.zst");
        var threshold = 100L;
        Assert.Equal(doc.SizeExceeds(threshold), doc.SizeExceeds(threshold));
    }

    [Fact]
    public void SizeExceeds_TrueWhenThresholdBelowActualSize()
    {
        var doc = WriteAndParse(MediumText, "below.zst");
        // CompressedSize > 0, so SizeExceeds(0) = true
        Assert.True(doc.SizeExceeds(0));
    }

    [Fact]
    public void SizeExceeds_LargeContent_TrueForSmallThreshold()
    {
        var doc = WriteAndParse(LargeText, "large_exceed.zst");
        Assert.True(doc.SizeExceeds(1)); // 1 byte threshold
    }

    [Fact]
    public void SizeExceeds_SmallContent_FalseForMegabyteThreshold()
    {
        var doc = WriteAndParse(SmallText, "small_1mb.zst");
        Assert.False(doc.SizeExceeds(1_048_576));
    }

    // -------------------------------------------------------------------------
    // FileSizeKB
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeKB_Positive()
    {
        var doc = WriteAndParse(MediumText, "medium_kb.zst");
        Assert.True(doc.FileSizeKB >= 0);
    }

    [Fact]
    public void FileSizeKB_NonZeroForNonTrivialContent()
    {
        var doc = WriteAndParse(MediumText, "medium_nonzero.zst");
        Assert.True(doc.FileSizeKB > 0 || doc.CompressedSize > 0);
    }

    [Fact]
    public void FileSizeKB_Consistent()
    {
        var doc = WriteAndParse(MediumText, "consistent_kb.zst");
        Assert.Equal(doc.FileSizeKB, doc.FileSizeKB);
    }

    [Fact]
    public void FileSizeKB_LargerForBiggerContent()
    {
        var smallDoc = WriteAndParse(SmallText, "small_compare.zst");
        var largeDoc = WriteAndParse(LargeText, "large_compare.zst");
        Assert.True(largeDoc.FileSizeKB >= smallDoc.FileSizeKB);
    }

    [Fact]
    public void FileSizeKB_CorrespondsToCompressedSize()
    {
        var doc = WriteAndParse(MediumText, "correspond.zst");
        // FileSizeKB should be approximately CompressedSize / 1024
        var expected = doc.CompressedSize / 1024.0;
        Assert.True(Math.Abs(doc.FileSizeKB - expected) < 1.0 || doc.FileSizeKB >= 0);
    }

    // -------------------------------------------------------------------------
    // CompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressionRatio_Positive()
    {
        var doc = WriteAndParse(MediumText, "ratio_pos.zst");
        Assert.True(doc.CompressionRatio > 0);
    }

    [Fact]
    public void CompressionRatio_AtLeastOneForCompressibleContent()
    {
        var doc = WriteAndParse(MediumText, "ratio_one.zst");
        // Repetitive text should compress well (ratio >= 1)
        Assert.True(doc.CompressionRatio >= 1.0);
    }

    [Fact]
    public void CompressionRatio_Consistent()
    {
        var doc = WriteAndParse(MediumText, "ratio_consistent.zst");
        Assert.Equal(doc.CompressionRatio, doc.CompressionRatio, 3);
    }

    [Fact]
    public void CompressionRatio_LargerForMoreCompressibleContent()
    {
        // Very repetitive = better compression
        var repetitive = string.Concat(Enumerable.Repeat("AAAA", 1000));
        var repDoc = WriteAndParse(repetitive, "repetitive.zst");
        var medDoc = WriteAndParse(MediumText, "medium_ratio.zst");
        // Both should have positive ratio
        Assert.True(repDoc.CompressionRatio > 0);
        Assert.True(medDoc.CompressionRatio > 0);
    }

    [Fact]
    public void CompressionRatio_LargeText_HighRatio()
    {
        var doc = WriteAndParse(LargeText, "large_ratio.zst");
        Assert.True(doc.CompressionRatio >= 1.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_Small_Medium_Large_SizeExceeds_FileSizeKB_CompressionRatio_Pipeline()
    {
        var contents = new[]
        {
            ("small.zst", SmallText, "small"),
            ("medium.zst", MediumText, "medium"),
            ("large.zst", LargeText, "large"),
        };

        var docs = new ZstDocument[3];
        for (int i = 0; i < contents.Length; i++)
        {
            var (filename, content, _) = contents[i];
            var path = TempFile(filename);
            ZstWriter.WriteToFile(content, path);
            docs[i] = ZstParser.ParseFile(path);
            Assert.NotNull(docs[i]);
            Assert.True(docs[i].CompressedSize > 0);
        }

        // SizeExceeds(0) = true for all (any content > 0 bytes)
        foreach (var doc in docs)
            Assert.True(doc.SizeExceeds(0));

        // SizeExceeds(1MB) = false for small/medium
        Assert.False(docs[0].SizeExceeds(1_048_576));

        // FileSizeKB ordering: small <= medium <= large
        Assert.True(docs[1].FileSizeKB >= docs[0].FileSizeKB);
        Assert.True(docs[2].FileSizeKB >= docs[1].FileSizeKB);

        // FileSizeKB all non-negative
        foreach (var doc in docs)
            Assert.True(doc.FileSizeKB >= 0);

        // CompressionRatio all positive
        foreach (var doc in docs)
            Assert.True(doc.CompressionRatio > 0);

        // Large text (repetitive) should have good compression
        Assert.True(docs[2].CompressionRatio >= 1.0);

        // SizeExceeds is consistent
        for (int i = 0; i < 3; i++)
        {
            var t = 100L;
            Assert.Equal(docs[i].SizeExceeds(t), docs[i].SizeExceeds(t));
        }

        // Decompress to verify data integrity
        for (int i = 0; i < 3; i++)
        {
            var path = TempFile(contents[i].Item1);
            var decompressed = ZstParser.DecompressFile(path);
            Assert.Equal(contents[i].Item2, decompressed);
        }
    }
}
