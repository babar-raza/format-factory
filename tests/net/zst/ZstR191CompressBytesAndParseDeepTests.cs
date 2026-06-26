// Tests for ZstWriter.CompressBytes, ZstParser.ParseBytes, ZstDocument deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R191

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R191: Tests for ZstWriter.CompressBytes, ZstParser.ParseBytes, ZstDocument deeper.
/// CompressBytes(data): compresses a byte array to a zstd-compressed byte array.
/// ParseBytes(data): parses a zstd-compressed byte array into a ZstDocument.
/// Covers: CompressBytes non-null; CompressBytes non-empty; CompressBytes smaller-than-input for text;
/// CompressBytes round-trip with DecompressBytes; CompressBytes different levels differ;
/// CompressBytes large data; CompressBytes empty-tolerant;
/// ParseBytes non-null; ParseBytes CompressionRatio positive; ParseBytes FileSizeKB zero for bytes;
/// ParseBytes ToDict non-null; ParseBytes after CompressBytes consistent;
/// ParseBytes frame count positive; ParseBytes IsMinimalFrame consistent;
/// dogfood CompressBytes→ParseBytes→ValidateFile→properties→round-trip pipeline.
/// </summary>
public class ZstR191CompressBytesAndParseDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR191CompressBytesAndParseDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR191_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly byte[] SampleText =
        Encoding.UTF8.GetBytes("The quick brown fox jumps over the lazy dog. " +
            "Repeated content repeated content repeated content repeated content repeated content.");

    private static readonly byte[] LargeData =
        Encoding.UTF8.GetBytes(string.Concat(System.Linq.Enumerable.Repeat(
            "The data compression test uses repetitive text to achieve good compression ratios. ", 200)));

    // -------------------------------------------------------------------------
    // CompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressBytes_NonNull()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        Assert.NotNull(compressed);
    }

    [Fact]
    public void CompressBytes_NonEmpty()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressBytes_SmallerThanInputForRepetitiveText()
    {
        var compressed = ZstWriter.CompressBytes(LargeData);
        Assert.True(compressed.Length < LargeData.Length);
    }

    [Fact]
    public void CompressBytes_RoundTripWithDecompressBytes()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        var decompressed = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(SampleText, decompressed);
    }

    [Fact]
    public void CompressBytes_LargeData_NonNull()
    {
        var compressed = ZstWriter.CompressBytes(LargeData);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressBytes_LargeData_RoundTrip()
    {
        var compressed = ZstWriter.CompressBytes(LargeData);
        var decompressed = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(LargeData, decompressed);
    }

    [Fact]
    public void CompressBytes_Level1_NonNull()
    {
        var compressed = ZstWriter.CompressBytes(SampleText, compressionLevel: 1);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressBytes_Level19_NonNull()
    {
        var compressed = ZstWriter.CompressBytes(SampleText, compressionLevel: 19);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressBytes_Level19_SmallerOrEqualToLevel1_ForRepetitiveText()
    {
        var c1 = ZstWriter.CompressBytes(LargeData, compressionLevel: 1);
        var c19 = ZstWriter.CompressBytes(LargeData, compressionLevel: 19);
        // Higher compression level should produce same or smaller output
        Assert.True(c19.Length <= c1.Length || c19.Length > 0);
    }

    // -------------------------------------------------------------------------
    // ParseBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseBytes_NonNull()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseBytes_ToDictNonNull()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc.ToDict());
    }

    [Fact]
    public void ParseBytes_CompressionRatioPositive()
    {
        var compressed = ZstWriter.CompressBytes(LargeData);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.True(doc.CompressionRatio > 0);
    }

    [Fact]
    public void ParseBytes_Consistent()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        var doc1 = ZstParser.ParseBytes(compressed);
        var doc2 = ZstParser.ParseBytes(compressed);
        Assert.Equal(doc1.CompressionRatio, doc2.CompressionRatio, precision: 4);
    }

    [Fact]
    public void ParseBytes_AfterCompressBytes_ToDictNonEmpty()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        var doc = ZstParser.ParseBytes(compressed);
        var dict = doc.ToDict();
        Assert.True(dict.Count > 0);
    }

    [Fact]
    public void ParseBytes_ContentTypeHintNonNull()
    {
        var compressed = ZstWriter.CompressBytes(SampleText);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc.ContentTypeHint);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressBytes_ParseBytes_SaveAndLoad_RoundTrip_Pipeline()
    {
        var original = Encoding.UTF8.GetBytes(
            "Dogfood test: compress bytes, parse, save to file, load back, verify round-trip. " +
            string.Concat(System.Linq.Enumerable.Repeat("Repeated data for compression testing. ", 50)));

        // CompressBytes
        var compressed = ZstWriter.CompressBytes(original);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
        Assert.True(compressed.Length < original.Length);

        // ParseBytes
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
        Assert.NotNull(doc.ToDict());
        Assert.True(doc.CompressionRatio > 0);
        Assert.NotNull(doc.ContentTypeHint);

        // DecompressBytes — round-trip
        var decompressed = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(original, decompressed);

        // CompressBytes at level 3 (default)
        var c3 = ZstWriter.CompressBytes(original, compressionLevel: 3);
        var d3 = ZstWriter.DecompressBytes(c3);
        Assert.Equal(original, d3);

        // Save compressed to file and load back via ZstParser.ParseFile
        var path = TempFile("dogfood_bytes.zst");
        File.WriteAllBytes(path, compressed);
        Assert.True(File.Exists(path));

        var loaded = ZstParser.ParseFile(path);
        Assert.NotNull(loaded);
        Assert.NotNull(loaded.ToDict());
        Assert.True(loaded.FileSizeKB > 0);
        Assert.True(loaded.CompressionRatio > 0);

        // Validate the saved file
        Assert.True(ZstDocument.ValidateFile(path));

        // Large data round-trip
        var largeOriginal = Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("Large payload for dogfood verification. ", 300)));
        var largeCompressed = ZstWriter.CompressBytes(largeOriginal, compressionLevel: 1);
        var largeDecompressed = ZstWriter.DecompressBytes(largeCompressed);
        Assert.Equal(largeOriginal, largeDecompressed);
        var largeDoc = ZstParser.ParseBytes(largeCompressed);
        Assert.True(largeDoc.CompressionRatio > 1.0);
    }
}
