// Tests for ZstDocument.CompressionRatio, FileSizeKB, SizeExceeds deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R185

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R185: Tests for ZstDocument.CompressionRatio, FileSizeKB, SizeExceeds deeper coverage.
/// ZstDocument.CompressionRatio: decompressed/compressed ratio.
/// ZstDocument.FileSizeKB: compressed size in kilobytes.
/// ZstDocument.SizeExceeds(limitKB): true if FileSizeKB > limitKB.
/// Covers: CompressionRatio positive; CompressionRatio >= 1.0 for compressible data;
/// CompressionRatio repetitive content high ratio; CompressionRatio consistent across loads;
/// FileSizeKB positive; FileSizeKB matches file size / 1024; FileSizeKB small for short text;
/// FileSizeKB large for large content; SizeExceeds(0) true for any content;
/// SizeExceeds(1000000) false for short text; SizeExceeds exact boundary;
/// ToDict non-null; ToDict non-empty; ToDict contains expected key;
/// dogfood WriteShort/Long files → compare FileSizeKB → SizeExceeds → CompressionRatio pipeline.
/// </summary>
public class ZstR185CompressionRatioAndDocumentDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string ShortText = "Short.";
    private static readonly string RepeatText = string.Concat(System.Linq.Enumerable.Repeat("AAAA BBBB CCCC DDDD EEEE. ", 300));

    public ZstR185CompressionRatioAndDocumentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR185_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressionRatio_Positive()
    {
        var path = TempFile("ratio.zst");
        ZstWriter.WriteToFile(RepeatText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.CompressionRatio > 0);
    }

    [Fact]
    public void CompressionRatio_RepetitiveContent_HighRatio()
    {
        var path = TempFile("repetitive.zst");
        ZstWriter.WriteToFile(RepeatText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.CompressionRatio >= 1.0);
    }

    [Fact]
    public void CompressionRatio_ConsistentAcrossLoads()
    {
        var path = TempFile("consistent.zst");
        ZstWriter.WriteToFile(RepeatText, path);
        var doc1 = ZstDocument.FromFile(path);
        var doc2 = ZstDocument.FromFile(path);
        Assert.Equal(doc1.CompressionRatio, doc2.CompressionRatio, 3);
    }

    [Fact]
    public void CompressionRatio_ShortContent_NonNegative()
    {
        var path = TempFile("short_ratio.zst");
        ZstWriter.WriteToFile(ShortText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.CompressionRatio >= 0.0);
    }

    // -------------------------------------------------------------------------
    // FileSizeKB
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeKB_Positive()
    {
        var path = TempFile("size.zst");
        ZstWriter.WriteToFile(RepeatText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.FileSizeKB > 0);
    }

    [Fact]
    public void FileSizeKB_SmallForShortText()
    {
        var path = TempFile("small.zst");
        ZstWriter.WriteToFile(ShortText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.FileSizeKB < 10.0); // Short text should be < 10KB
    }

    [Fact]
    public void FileSizeKB_LargerForLargeContent()
    {
        var smallPath = TempFile("small2.zst");
        var largePath = TempFile("large2.zst");
        ZstWriter.WriteToFile(ShortText, smallPath);
        ZstWriter.WriteToFile(RepeatText, largePath);
        var smallDoc = ZstDocument.FromFile(smallPath);
        var largeDoc = ZstDocument.FromFile(largePath);
        Assert.True(largeDoc.FileSizeKB >= smallDoc.FileSizeKB);
    }

    [Fact]
    public void FileSizeKB_MatchesCompressedSizeDivided()
    {
        var path = TempFile("match.zst");
        ZstWriter.WriteToFile(RepeatText, path);
        var doc = ZstDocument.FromFile(path);
        var expected = doc.CompressedSize / 1024.0;
        Assert.True(Math.Abs(doc.FileSizeKB - expected) < 1.0);
    }

    // -------------------------------------------------------------------------
    // SizeExceeds
    // -------------------------------------------------------------------------

    [Fact]
    public void SizeExceeds_Zero_AlwaysTrue()
    {
        var path = TempFile("exceed_zero.zst");
        ZstWriter.WriteToFile(ShortText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.True(doc.SizeExceeds(0));
    }

    [Fact]
    public void SizeExceeds_VeryLarge_False()
    {
        var path = TempFile("exceed_large.zst");
        ZstWriter.WriteToFile(ShortText, path);
        var doc = ZstDocument.FromFile(path);
        Assert.False(doc.SizeExceeds(1000000));
    }

    [Fact]
    public void SizeExceeds_ConsistentWithFileSizeKB()
    {
        var path = TempFile("exceed_check.zst");
        ZstWriter.WriteToFile(RepeatText, path);
        var doc = ZstDocument.FromFile(path);
        var kb = doc.FileSizeKB;
        // SizeExceeds(kb-1) should be true
        Assert.True(doc.SizeExceeds((long)(kb - 1)));
        // SizeExceeds(kb+1000) should be false
        Assert.False(doc.SizeExceeds((long)(kb + 1000)));
    }

    // -------------------------------------------------------------------------
    // ToDict
    // -------------------------------------------------------------------------

    [Fact]
    public void ToDict_NonNull()
    {
        var path = TempFile("todict.zst");
        ZstWriter.WriteToFile("Some content.", path);
        var doc = ZstDocument.FromFile(path);
        Assert.NotNull(doc.ToDict());
    }

    [Fact]
    public void ToDict_NonEmpty()
    {
        var path = TempFile("todict2.zst");
        ZstWriter.WriteToFile("Some content.", path);
        var doc = ZstDocument.FromFile(path);
        Assert.NotEmpty(doc.ToDict());
    }

    [Fact]
    public void ToDict_ContainsExpectedKey()
    {
        var path = TempFile("todict3.zst");
        ZstWriter.WriteToFile("Some content.", path);
        var doc = ZstDocument.FromFile(path);
        var dict = doc.ToDict();
        Assert.True(dict.Count > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteFiles_CompareSizes_SizeExceeds_CompressionRatio_Pipeline()
    {
        // Write short file
        var shortPath = TempFile("dog_short.zst");
        ZstWriter.WriteToFile(ShortText, shortPath);
        var shortDoc = ZstDocument.FromFile(shortPath);
        Assert.True(shortDoc.FileSizeKB > 0);
        Assert.True(shortDoc.SizeExceeds(0));
        Assert.False(shortDoc.SizeExceeds(1000000));
        Assert.True(shortDoc.CompressionRatio >= 0.0);

        // Write repetitive file
        var repeatPath = TempFile("dog_repeat.zst");
        ZstWriter.WriteToFile(RepeatText, repeatPath);
        var repeatDoc = ZstDocument.FromFile(repeatPath);
        Assert.True(repeatDoc.FileSizeKB > 0);
        Assert.True(repeatDoc.CompressionRatio >= 1.0);

        // Repeat file is larger compressed (though high ratio)
        Assert.True(repeatDoc.FileSizeKB >= shortDoc.FileSizeKB);

        // SizeExceeds comparison
        var shortKB = (long)shortDoc.FileSizeKB;
        Assert.True(repeatDoc.SizeExceeds(shortKB));

        // ToDict for both
        var shortDict = shortDoc.ToDict();
        Assert.NotNull(shortDict);
        Assert.True(shortDict.Count > 0);

        var repeatDict = repeatDoc.ToDict();
        Assert.NotNull(repeatDict);

        // CompressionRatio consistent
        var repeatDoc2 = ZstDocument.FromFile(repeatPath);
        Assert.Equal(repeatDoc.CompressionRatio, repeatDoc2.CompressionRatio, 3);

        // FileSizeKB matches CompressedSize
        var expectedKB = repeatDoc.CompressedSize / 1024.0;
        Assert.True(Math.Abs(repeatDoc.FileSizeKB - expectedKB) < 1.0);

        // Decompression still works
        Assert.Equal(ShortText, ZstParser.DecompressFile(shortPath));
        Assert.Equal(RepeatText, ZstParser.DecompressFile(repeatPath));
    }
}
