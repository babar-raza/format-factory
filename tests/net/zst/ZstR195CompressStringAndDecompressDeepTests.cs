// Tests for ZstWriter.CompressString, DecompressString, ValidateBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R195

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R195: Tests for ZstWriter.CompressString, DecompressString, ValidateBytes deeper.
/// CompressString(text): compresses a string to a zstd-compressed byte array.
/// DecompressString(data): decompresses a zstd byte array back to a string.
/// ValidateBytes(data): checks if a byte array is a valid zstd frame.
/// Covers: CompressString non-null; CompressString non-empty; CompressString round-trip;
/// CompressString smaller for repetitive text; CompressString with encoding;
/// CompressString then ParseBytes; CompressString persist;
/// DecompressString non-null; DecompressString matches original;
/// DecompressString after CompressString consistent; DecompressString large text;
/// ValidateBytes true for compressed; ValidateBytes false for garbage;
/// ValidateBytes true for file-read bytes; ValidateBytes non-null not-throw;
/// dogfood CompressString→DecompressString→ValidateBytes→ParseBytes pipeline.
/// </summary>
public class ZstR195CompressStringAndDecompressDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR195CompressStringAndDecompressDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR195_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ShortText = "Hello, world! This is a test of zstd string compression.";

    private static readonly string RepetitiveText =
        string.Concat(System.Linq.Enumerable.Repeat(
            "The quick brown fox jumps over the lazy dog. ", 100));

    private static readonly string LargeText =
        string.Concat(System.Linq.Enumerable.Repeat(
            "Compression test data with varied content for validation purposes. ", 200));

    // -------------------------------------------------------------------------
    // CompressString
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_NonNull()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        Assert.NotNull(compressed);
    }

    [Fact]
    public void CompressString_NonEmpty()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressString_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        var decompressed = ZstWriter.DecompressString(compressed);
        Assert.Equal(ShortText, decompressed);
    }

    [Fact]
    public void CompressString_SmallerForRepetitiveText()
    {
        var compressed = ZstWriter.CompressString(RepetitiveText);
        var original = Encoding.UTF8.GetBytes(RepetitiveText);
        Assert.True(compressed.Length < original.Length);
    }

    [Fact]
    public void CompressString_LargeText_NonNull()
    {
        var compressed = ZstWriter.CompressString(LargeText);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressString_LargeText_RoundTrip()
    {
        var compressed = ZstWriter.CompressString(LargeText);
        var decompressed = ZstWriter.DecompressString(compressed);
        Assert.Equal(LargeText, decompressed);
    }

    [Fact]
    public void CompressString_ThenParseBytes_NonNull()
    {
        var compressed = ZstWriter.CompressString(RepetitiveText);
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
    }

    [Fact]
    public void CompressString_Persist()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        var path = TempFile("compress_string.zst");
        File.WriteAllBytes(path, compressed);
        Assert.True(File.Exists(path));
        var loaded = File.ReadAllBytes(path);
        Assert.Equal(compressed, loaded);
    }

    [Fact]
    public void CompressString_WithLevel1_NonNull()
    {
        var compressed = ZstWriter.CompressString(RepetitiveText, compressionLevel: 1);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    [Fact]
    public void CompressString_WithLevel9_NonNull()
    {
        var compressed = ZstWriter.CompressString(RepetitiveText, compressionLevel: 9);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
    }

    // -------------------------------------------------------------------------
    // DecompressString
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressString_NonNull()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        Assert.NotNull(ZstWriter.DecompressString(compressed));
    }

    [Fact]
    public void DecompressString_MatchesOriginal()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        Assert.Equal(ShortText, ZstWriter.DecompressString(compressed));
    }

    [Fact]
    public void DecompressString_Consistent()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        var d1 = ZstWriter.DecompressString(compressed);
        var d2 = ZstWriter.DecompressString(compressed);
        Assert.Equal(d1, d2);
    }

    [Fact]
    public void DecompressString_LargeText_Matches()
    {
        var compressed = ZstWriter.CompressString(LargeText);
        var decompressed = ZstWriter.DecompressString(compressed);
        Assert.Equal(LargeText, decompressed);
    }

    [Fact]
    public void DecompressString_AfterFileRoundTrip_Matches()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        var path = TempFile("rt_string.zst");
        File.WriteAllBytes(path, compressed);
        var fromFile = File.ReadAllBytes(path);
        Assert.Equal(ShortText, ZstWriter.DecompressString(fromFile));
    }

    // -------------------------------------------------------------------------
    // ValidateBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidateBytes_TrueForCompressed()
    {
        var compressed = ZstWriter.CompressString(ShortText);
        Assert.True(ZstWriter.ValidateBytes(compressed));
    }

    [Fact]
    public void ValidateBytes_FalseForGarbage()
    {
        var garbage = new byte[] { 0x00, 0x01, 0x02, 0x03, 0x04 };
        Assert.False(ZstWriter.ValidateBytes(garbage));
    }

    [Fact]
    public void ValidateBytes_TrueForFileReadBytes()
    {
        var compressed = ZstWriter.CompressString(RepetitiveText);
        var path = TempFile("validate_file.zst");
        File.WriteAllBytes(path, compressed);
        var fromFile = File.ReadAllBytes(path);
        Assert.True(ZstWriter.ValidateBytes(fromFile));
    }

    [Fact]
    public void ValidateBytes_CompressBytes_AlsoValid()
    {
        var bytes = Encoding.UTF8.GetBytes(ShortText);
        var compressed = ZstWriter.CompressBytes(bytes);
        Assert.True(ZstWriter.ValidateBytes(compressed));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressString_DecompressString_ValidateBytes_ParseBytes_Pipeline()
    {
        var original = "Dogfood verification text for zstd string compression. " +
            string.Concat(System.Linq.Enumerable.Repeat("Repeated content for compression. ", 30));

        // CompressString
        var compressed = ZstWriter.CompressString(original);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
        Assert.True(compressed.Length < Encoding.UTF8.GetBytes(original).Length);

        // ValidateBytes
        Assert.True(ZstWriter.ValidateBytes(compressed));

        // DecompressString
        var decompressed = ZstWriter.DecompressString(compressed);
        Assert.Equal(original, decompressed);

        // ParseBytes
        var doc = ZstParser.ParseBytes(compressed);
        Assert.NotNull(doc);
        Assert.True(doc.CompressionRatio > 0);

        // Different levels
        var c1 = ZstWriter.CompressString(original, compressionLevel: 1);
        var c9 = ZstWriter.CompressString(original, compressionLevel: 9);
        Assert.True(ZstWriter.ValidateBytes(c1));
        Assert.True(ZstWriter.ValidateBytes(c9));
        Assert.Equal(original, ZstWriter.DecompressString(c1));
        Assert.Equal(original, ZstWriter.DecompressString(c9));

        // Save to file and validate
        var path = TempFile("dogfood_compress_string.zst");
        File.WriteAllBytes(path, compressed);
        Assert.True(File.Exists(path));
        Assert.True(ZstDocument.ValidateFile(path));

        // Load back and decompress
        var fromFile = File.ReadAllBytes(path);
        Assert.True(ZstWriter.ValidateBytes(fromFile));
        var fromFileStr = ZstWriter.DecompressString(fromFile);
        Assert.Equal(original, fromFileStr);

        // ParseFile
        var parsedFromFile = ZstParser.ParseFile(path);
        Assert.NotNull(parsedFromFile);
        Assert.True(parsedFromFile.FileSizeKB > 0);
        Assert.True(parsedFromFile.CompressionRatio > 0);

        // Large text consistency
        var largeCompressed = ZstWriter.CompressString(LargeText);
        Assert.True(ZstWriter.ValidateBytes(largeCompressed));
        var largeDecompressed = ZstWriter.DecompressString(largeCompressed);
        Assert.Equal(LargeText, largeDecompressed);
    }
}
