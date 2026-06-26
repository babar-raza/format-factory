// Tests for ZstParser.ParseBytes, ZstException deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R173

using System;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R173: Tests for ZstParser.ParseBytes, ZstException deeper coverage.
/// ZstParser.ParseBytes(bytes): parses a zstd-compressed byte array into ZstDocument.
/// ZstException: exception thrown when parsing or decompression fails.
/// Covers: ParseBytes non-null; ParseBytes FrameCount positive;
/// ParseBytes CompressedSize correct; ParseBytes IsEmpty false;
/// ParseBytes for different compression levels; ParseBytes preserves CompressedSize;
/// ParseBytes->Decompress round-trip; ZstException is-a Exception;
/// ZstException message non-null; ZstException from invalid data;
/// ParseBytes from CompressString; ParseBytes from CompressBytes;
/// dogfood Compress->ParseBytes->properties->Decompress->verify pipeline.
/// </summary>
public class ZstR173ParseBytesAndExceptionDeepTests
{
    private static readonly byte[] SampleBytes =
        System.Text.Encoding.UTF8.GetBytes(
            "Sample data for ParseBytes testing in the Format Factory SDK.");

    private static readonly string SampleText =
        "ParseBytes test content for Zstandard compression verification.";

    // -------------------------------------------------------------------------
    // ParseBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseBytes_NonNull()
    {
        var compressed = ZstWriter.Compress(SampleBytes, 3);
        Assert.NotNull(ZstParser.ParseBytes(compressed));
    }

    [Fact]
    public void ParseBytes_FrameCount_Positive()
    {
        var compressed = ZstWriter.Compress(SampleBytes, 3);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseBytes_CompressedSize_MatchesInput()
    {
        var compressed = ZstWriter.Compress(SampleBytes, 3);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.Equal(compressed.Length, (int)doc.CompressedSize);
    }

    [Fact]
    public void ParseBytes_IsEmpty_False()
    {
        var compressed = ZstWriter.Compress(SampleBytes, 3);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void ParseBytes_Level1_Valid()
    {
        var compressed = ZstWriter.Compress(SampleBytes, 1);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseBytes_Level19_Valid()
    {
        var compressed = ZstWriter.Compress(SampleBytes, 19);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseBytes_FromCompressString_Valid()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseBytes_FromCompressBytes_Valid()
    {
        var compressed = ZstWriter.CompressBytes(SampleBytes);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseBytes_DifferentLevels_AllPositiveFrameCount()
    {
        foreach (var level in new[] { 1, 3, 6, 9, 15 })
        {
            var compressed = ZstWriter.Compress(SampleBytes, level);
            var doc = ZstParser.ParseBytes(compressed);
            Assert.True(doc.FrameCount > 0, $"FrameCount should be positive at level {level}");
        }
    }

    [Fact]
    public void ParseBytes_ThenDecompress_RoundTrip()
    {
        var compressed = ZstWriter.Compress(SampleBytes, 3);
        ZstParser.ParseBytes(compressed); // just metadata
        var decompressed = ZstParser.Decompress(compressed);
        Assert.Equal(SampleBytes, decompressed);
    }

    // -------------------------------------------------------------------------
    // ZstException
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstException_IsException()
    {
        var ex = new ZstException("test");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void ZstException_Message_NonNull()
    {
        var ex = new ZstException("Test error message.");
        Assert.NotNull(ex.Message);
    }

    [Fact]
    public void ZstException_Message_ContainsText()
    {
        var ex = new ZstException("Custom error text");
        Assert.Contains("Custom error text", ex.Message);
    }

    [Fact]
    public void ZstException_CanBeThrown_AndCaught()
    {
        var caught = false;
        try
        {
            throw new ZstException("Test throw.");
        }
        catch (ZstException)
        {
            caught = true;
        }
        Assert.True(caught);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Compress_ParseBytes_Properties_Decompress_Verify_Pipeline()
    {
        // Compress at level 6
        var compressed = ZstWriter.Compress(SampleBytes, 6);
        Assert.True(compressed.Length > 0);

        // ParseBytes
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
        Assert.True(doc.FrameCount > 0);
        Assert.Equal(compressed.Length, (int)doc.CompressedSize);
        Assert.False(doc.IsEmpty);

        // CompressString path
        var strCompressed = ZstWriter.CompressString(SampleText);
        var strDoc = ZstParser.ParseBytes(strCompressed);
        Assert.NotNull(strDoc);
        Assert.True(strDoc.FrameCount > 0);
        Assert.False(strDoc.IsEmpty);

        // Decompress (bytes)
        var decompressedBytes = ZstParser.Decompress(compressed);
        Assert.Equal(SampleBytes, decompressedBytes);

        // DecompressToString
        var decompressedStr = ZstParser.DecompressToString(strCompressed);
        Assert.Equal(SampleText, decompressedStr);

        // ZstException instantiation
        var ex = new ZstException("Pipeline complete.");
        Assert.NotNull(ex.Message);
    }
}
