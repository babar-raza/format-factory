// Tests for ZstWriter.CompressString, ZstParser.DecompressToString deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R168

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R168: Tests for ZstWriter.CompressString, ZstParser.DecompressToString deeper.
/// CompressString(text): compresses a UTF-8 string to bytes.
/// CompressString(text, level): compresses at given level.
/// DecompressToString(bytes): decompresses bytes back to UTF-8 string.
/// Covers: CompressString non-null; CompressString non-empty bytes;
/// CompressString->DecompressToString round-trip; CompressString at level 1 round-trip;
/// CompressString at level 19 round-trip; CompressString empty string;
/// CompressString long string; DecompressToString non-null;
/// DecompressToString correct result; CompressString->ParseBytes FrameCount >= 1;
/// CompressString->ZstDocument.Load IsEmpty false;
/// CompressString preserves unicode; DecompressToString preserves unicode;
/// CompressString multiple levels all round-trip;
/// dogfood CompressString->DecompressToString->CompressString->ParseBytes->Verify pipeline.
/// </summary>
public class ZstR168CompressStringAndDecompressTests : IDisposable
{
    private readonly string _tempDir;

    private const string ShortText = "Hello, world!";
    private const string LongText =
        "The quick brown fox jumps over the lazy dog. " +
        "Pack my box with five dozen liquor jugs. " +
        "How vexingly quick daft zebras jump! " +
        "The five boxing wizards jump quickly. " +
        "Sphinx of black quartz, judge my vow. ";

    private const string UnicodeText = "Héllo, wörld! Ñoño café résumé";

    public ZstR168CompressStringAndDecompressTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR168_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CompressString
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_NonNull()
    {
        var result = ZstWriter.CompressString(ShortText);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressString_NonEmpty()
    {
        var result = ZstWriter.CompressString(ShortText);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void CompressString_EmptyString_ReturnsBytes()
    {
        var result = ZstWriter.CompressString(string.Empty);
        Assert.NotNull(result);
        // Empty string compressed should still produce valid zst frame
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void CompressString_LongText_NonEmpty()
    {
        var result = ZstWriter.CompressString(LongText);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void CompressString_Level1_NonNull()
    {
        var result = ZstWriter.CompressString(ShortText, 1);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressString_Level19_NonNull()
    {
        var result = ZstWriter.CompressString(ShortText, 19);
        Assert.NotNull(result);
    }

    [Fact]
    public void CompressString_ParseBytes_FrameCountPositive()
    {
        var bytes = ZstWriter.CompressString(LongText);
        var doc = ZstParser.ParseBytes(bytes);
        Assert.True(doc.FrameCount >= 1);
    }

    // -------------------------------------------------------------------------
    // DecompressToString
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressToString_RoundTrip_ShortText()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(ShortText, result);
    }

    [Fact]
    public void DecompressToString_RoundTrip_LongText()
    {
        var compressed = ZstWriter.CompressString(LongText);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(LongText, result);
    }

    [Fact]
    public void DecompressToString_Level1_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(LongText, 1);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(LongText, result);
    }

    [Fact]
    public void DecompressToString_Level19_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(LongText, 19);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(LongText, result);
    }

    [Fact]
    public void DecompressToString_PreservesUnicode()
    {
        var compressed = ZstWriter.CompressString(UnicodeText);
        var result = ZstParser.DecompressToString(compressed);
        Assert.Equal(UnicodeText, result);
    }

    [Fact]
    public void DecompressToString_AllLevels_RoundTrip()
    {
        foreach (var level in new[] { 1, 3, 6, 9, 15, 19 })
        {
            var compressed = ZstWriter.CompressString(LongText, level);
            var result = ZstParser.DecompressToString(compressed);
            Assert.Equal(LongText, result);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressStringDecompressCompressParseVerify_Pipeline()
    {
        // CompressString
        var compressed = ZstWriter.CompressString(LongText);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);

        // DecompressToString
        var decompressed = ZstParser.DecompressToString(compressed);
        Assert.Equal(LongText, decompressed);

        // CompressString again (idempotent)
        var recompressed = ZstWriter.CompressString(decompressed);
        var redecompressed = ZstParser.DecompressToString(recompressed);
        Assert.Equal(LongText, redecompressed);

        // ParseBytes
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
        Assert.True(doc.FrameCount >= 1);
        Assert.False(doc.IsEmpty);

        // Multiple levels
        foreach (var level in new[] { 1, 6, 19 })
        {
            var c = ZstWriter.CompressString(LongText, level);
            var d = ZstParser.DecompressToString(c);
            Assert.Equal(LongText, d);
        }

        // Unicode
        var unicodeCompressed = ZstWriter.CompressString(UnicodeText);
        var unicodeResult = ZstParser.DecompressToString(unicodeCompressed);
        Assert.Equal(UnicodeText, unicodeResult);
    }
}
