// Tests for ZstParser.Decompress, DecompressToString chain and multi-input deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R170

using System;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R170: Tests for ZstParser.Decompress, DecompressToString chain and multi-input deeper.
/// Decompress(data): decompresses a byte array to the original bytes.
/// DecompressToString(data): decompresses a byte array to a UTF-8 string.
/// Covers: Decompress non-null; Decompress round-trip matches original bytes;
/// Decompress multi-input restores same bytes; Decompress at different levels round-trips;
/// DecompressToString non-null; DecompressToString round-trip matches original;
/// DecompressToString unicode preserved; DecompressToString empty string;
/// DecompressToString long text; Compress->Decompress->Compress->Decompress double round-trip;
/// CompressString->DecompressToString->CompressString->DecompressToString idempotent;
/// dogfood CompressString->Decompress->toString verify->DecompressToString verify pipeline.
/// </summary>
public class ZstR170DecompressAndCompressStringChainTests
{
    private static readonly string ShortText = "Hello, Zstandard!";
    private static readonly string LongText = string.Concat(
        "The quick brown fox jumps over the lazy dog. ",
        "Pack my box with five dozen liquor jugs. ",
        "How vexingly quick daft zebras jump! ",
        "The five boxing wizards jump quickly. ");

    private static readonly string UnicodeText =
        "Héllo Wörld — Привет мир — 你好世界 — مرحبا بالعالم";

    // -------------------------------------------------------------------------
    // Decompress (bytes)
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_NonNull()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        var result = ZstParser.Decompress(compressed);
        Assert.NotNull(result);
    }

    [Fact]
    public void Decompress_RoundTrip_MatchesOriginalBytes()
    {
        var originalBytes = Encoding.UTF8.GetBytes(ShortText);
        var compressed = ZstWriter.Compress(originalBytes, 3);
        var decompressed = ZstParser.Decompress(compressed);
        Assert.Equal(originalBytes, decompressed);
    }

    [Fact]
    public void Decompress_Level1_RoundTrip()
    {
        var originalBytes = Encoding.UTF8.GetBytes(LongText);
        var compressed = ZstWriter.Compress(originalBytes, 1);
        var decompressed = ZstParser.Decompress(compressed);
        Assert.Equal(originalBytes, decompressed);
    }

    [Fact]
    public void Decompress_Level19_RoundTrip()
    {
        var originalBytes = Encoding.UTF8.GetBytes(LongText);
        var compressed = ZstWriter.Compress(originalBytes, 19);
        var decompressed = ZstParser.Decompress(compressed);
        Assert.Equal(originalBytes, decompressed);
    }

    [Fact]
    public void Decompress_DoubleRoundTrip_Idempotent()
    {
        var originalBytes = Encoding.UTF8.GetBytes(ShortText);
        var c1 = ZstWriter.Compress(originalBytes, 3);
        var d1 = ZstParser.Decompress(c1);
        var c2 = ZstWriter.Compress(d1, 3);
        var d2 = ZstParser.Decompress(c2);
        Assert.Equal(originalBytes, d2);
    }

    // -------------------------------------------------------------------------
    // DecompressToString
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressToString_NonNull()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        Assert.NotNull(ZstParser.DecompressToString(compressed));
    }

    [Fact]
    public void DecompressToString_RoundTrip_MatchesOriginal()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(ShortText, result);
    }

    [Fact]
    public void DecompressToString_LongText_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(LongText);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(LongText, result);
    }

    [Fact]
    public void DecompressToString_Unicode_Preserved()
    {
        var compressed = ZstWriter.CompressString(UnicodeText);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(UnicodeText, result);
    }

    [Fact]
    public void DecompressToString_EmptyString_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(string.Empty);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void CompressString_DecompressToString_DoubleRoundTrip()
    {
        var c1 = ZstWriter.CompressString(ShortText);
        var d1 = ZstParser.DecompressToString(c1);
        var c2 = ZstWriter.CompressString(d1);
        var d2 = ZstParser.DecompressToString(c2);
        Assert.Equal(ShortText, d2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressStringDecompressBytesVerifyDecompressToStringVerify_Pipeline()
    {
        // CompressString
        var compressed = ZstWriter.CompressString(LongText);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);

        // Decompress (bytes path)
        var originalBytes = Encoding.UTF8.GetBytes(LongText);
        var decompressedBytes = ZstParser.Decompress(compressed);
        Assert.Equal(originalBytes.Length, decompressedBytes.Length);
        Assert.Equal(originalBytes, decompressedBytes);

        // Confirm string conversion
        var fromBytes = Encoding.UTF8.GetString(decompressedBytes);
        Assert.Equal(LongText, fromBytes);

        // DecompressToString (string path)
        var decompressedStr = ZstParser.DecompressToString(compressed);
        Assert.Equal(LongText, decompressedStr);

        // Unicode round-trip
        var unicodeCompressed = ZstWriter.CompressString(UnicodeText);
        var unicodeResult = ZstParser.DecompressToString(unicodeCompressed);
        Assert.Equal(UnicodeText, unicodeResult);

        // Double round-trip idempotency
        var c2 = ZstWriter.CompressString(decompressedStr);
        var d2 = ZstParser.DecompressToString(c2);
        Assert.Equal(LongText, d2);
    }
}
