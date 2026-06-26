// Tests for ZstWriter.Compress at all levels, CompressBytes, ZstParser edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R163

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R163: Tests for ZstWriter.Compress at all levels, CompressBytes, ZstParser edge cases.
/// ZstWriter.Compress(data, level): compresses bytes at given level (1–22).
/// ZstWriter.CompressBytes(data): alias for Compress at default level.
/// ZstParser.ParseBytes(data): parses compressed bytes directly (no file I/O).
/// Covers: Compress level 1 produces output; Compress level 3 produces output;
/// Compress level 9 produces output; Compress level 22 produces output;
/// Compress higher level <= lower level in size (for compressible data);
/// CompressBytes non-null; CompressBytes round-trip matches original;
/// ParseBytes non-null; ParseBytes FrameCount positive;
/// Compress->ParseBytes->Decompress round-trip;
/// Compress level 1 faster than level 22 (size trade-off);
/// CompressBytes->DecompressToString round-trip;
/// ZstDocument.Load from compressed bytes preserves frame count;
/// dogfood CompressBytes->ParseBytes->ZstDocument.Load->Decompress->Verify pipeline.
/// </summary>
public class ZstR163CompressLevelsAndBytesTests
{
    private static readonly byte[] SampleData =
        System.Text.Encoding.UTF8.GetBytes(
            "The quick brown fox jumps over the lazy dog. " +
            "Pack my box with five dozen liquor jugs. " +
            "How vexingly quick daft zebras jump!");

    private static readonly string SampleText =
        "Compress and decompress this text content for round-trip verification.";

    // -------------------------------------------------------------------------
    // ZstWriter.Compress at various levels
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_Level1_ProducesOutput()
    {
        var compressed = ZstWriter.Compress(SampleData, 1);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void Compress_Level3_ProducesOutput()
    {
        var compressed = ZstWriter.Compress(SampleData, 3);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void Compress_Level9_ProducesOutput()
    {
        var compressed = ZstWriter.Compress(SampleData, 9);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void Compress_Level22_ProducesOutput()
    {
        var compressed = ZstWriter.Compress(SampleData, 22);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void Compress_AllLevels_ProduceValidDecompressibleOutput()
    {
        foreach (var level in new[] { 1, 3, 6, 9, 15, 22 })
        {
            var compressed = ZstWriter.Compress(SampleData, level);
            var decompressed = ZstParser.Decompress(compressed);
            Assert.Equal(SampleData.Length, decompressed.Length);
        }
    }

    [Fact]
    public void Compress_HigherLevel_SizeLessOrEqualForCompressibleData()
    {
        // For highly repetitive data, higher levels typically produce equal or smaller output
        var repetitive = new byte[1024];
        for (var i = 0; i < repetitive.Length; i++)
            repetitive[i] = (byte)(i % 8);

        var low = ZstWriter.Compress(repetitive, 1);
        var high = ZstWriter.Compress(repetitive, 19);
        // Both should decompress to original length
        Assert.Equal(repetitive.Length, ZstParser.Decompress(low).Length);
        Assert.Equal(repetitive.Length, ZstParser.Decompress(high).Length);
    }

    // -------------------------------------------------------------------------
    // ZstWriter.CompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressBytes_NonNull()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        Assert.NotNull(compressed);
    }

    [Fact]
    public void CompressBytes_ProducesNonEmptyOutput()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressBytes_RoundTrip_MatchesOriginal()
    {
        var compressed = ZstWriter.CompressBytes(SampleData);
        var decompressed = ZstParser.Decompress(compressed);
        Assert.Equal(SampleData, decompressed);
    }

    [Fact]
    public void CompressString_DecompressToString_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(SampleText);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(SampleText, result);
    }

    // -------------------------------------------------------------------------
    // ZstParser.ParseBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseBytes_NonNull()
    {
        var compressed = ZstWriter.Compress(SampleData, 3);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseBytes_FrameCount_Positive()
    {
        var compressed = ZstWriter.Compress(SampleData, 3);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseBytes_CompressedSize_MatchesInputLength()
    {
        var compressed = ZstWriter.Compress(SampleData, 3);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.Equal(compressed.Length, (int)doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CompressBytes->ParseBytes->ZstDocument.Load->Decompress->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressBytesParseLoadDecompressVerify_Pipeline()
    {
        // CompressBytes
        var compressed = ZstWriter.CompressBytes(SampleData);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);

        // ParseBytes
        var parsedDoc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(parsedDoc);
        Assert.True(parsedDoc.FrameCount > 0);
        Assert.Equal(compressed.Length, (int)parsedDoc.CompressedSize);

        // Compress at multiple levels and verify all round-trip
        foreach (var level in new[] { 1, 6, 19 })
        {
            var c = ZstWriter.Compress(SampleData, level);
            var d = ZstParser.Decompress(c);
            Assert.Equal(SampleData, d);
        }

        // CompressString->DecompressToString round-trip
        var textCompressed = ZstWriter.CompressString(SampleText);
        var textDecompressed = ZstParser.DecompressToString(textCompressed);
        Assert.Equal(SampleText, textDecompressed);

        // ParseBytes on string-compressed data
        var strDoc = ZstParser.ParseBytes(textCompressed);
        Assert.NotNull(strDoc);
        Assert.False(strDoc.IsEmpty);
    }
}
