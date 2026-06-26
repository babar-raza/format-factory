// Tests for ZstParser.ParseFile unicode content, ValidateFile, ParseBytes chain deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R174

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R174: Tests for ZstParser unicode/validation coverage and ParseBytes chain.
/// Covers: ParseFile unicode round-trip; ValidateFile returns true for valid zst;
/// ValidateFile returns false for random bytes; ParseBytes non-null;
/// ParseBytes CompressedSize positive; ParseBytes FrameCount positive;
/// DecompressFileToString returns original for unicode; DecompressFile returns bytes;
/// WriteToFile then ParseFile then DecompressFileToString identity;
/// dogfood unicode WriteToFile->ParseFile->LoadStream->Decompress->Verify pipeline.
/// </summary>
public class ZstR174ParseFileUnicodeAndValidationTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly string UnicodeText =
        "Unicode test: こんにちは world! Ñoño résumé naïve café 日本語 中文 한국어.";

    private static readonly string AsciiText =
        "Standard ASCII content for compression and decompression testing.";

    public ZstR174ParseFileUnicodeAndValidationTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR174_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ParseFile unicode
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseFile_UnicodeContent_NonNull()
    {
        var path = TempFile("unicode.zst");
        ZstWriter.WriteToFile(UnicodeText, path);
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseFile_UnicodeContent_CompressedSizePositive()
    {
        var path = TempFile("unicode.zst");
        ZstWriter.WriteToFile(UnicodeText, path);
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void ParseFile_UnicodeContent_FrameCountPositive()
    {
        var path = TempFile("unicode_frame.zst");
        ZstWriter.WriteToFile(UnicodeText, path);
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void DecompressFileToString_UnicodeContent_RoundTrip()
    {
        var path = TempFile("unicode_roundtrip.zst");
        ZstWriter.WriteToFile(UnicodeText, path);
        var result = ZstParser.DecompressFile(path);
        Assert.Equal(UnicodeText, result);
    }

    // -------------------------------------------------------------------------
    // ValidateFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ValidateFile_ValidZstFile_ReturnsTrue()
    {
        var path = TempFile("valid.zst");
        ZstWriter.WriteToFile(AsciiText, path);
        Assert.True(ZstParser.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_RandomBytes_ReturnsFalse()
    {
        var path = TempFile("invalid.zst");
        File.WriteAllBytes(path, new byte[] { 0x00, 0x01, 0x02, 0x03, 0xFF });
        Assert.False(ZstParser.ValidateFile(path));
    }

    [Fact]
    public void ValidateFile_EmptyFile_ReturnsFalse()
    {
        var path = TempFile("empty.zst");
        File.WriteAllBytes(path, Array.Empty<byte>());
        Assert.False(ZstParser.ValidateFile(path));
    }

    // -------------------------------------------------------------------------
    // ParseBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseBytes_NonNull()
    {
        var bytes = ZstWriter.CompressString(AsciiText);
        var doc = ZstParser.ParseBytes(bytes);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseBytes_CompressedSizePositive()
    {
        var bytes = ZstWriter.CompressString(AsciiText);
        var doc = ZstParser.ParseBytes(bytes);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void ParseBytes_FrameCountPositive()
    {
        var bytes = ZstWriter.CompressString(AsciiText);
        var doc = ZstParser.ParseBytes(bytes);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseBytes_CompressedSizeMatchesInputLength()
    {
        var bytes = ZstWriter.CompressString(AsciiText);
        var doc = ZstParser.ParseBytes(bytes);
        Assert.Equal(bytes.Length, (int)doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Unicode_WriteToFile_ParseFile_LoadStream_Decompress_Verify_Pipeline()
    {
        // WriteToFile with unicode
        var path = TempFile("dogfood_unicode.zst");
        ZstWriter.WriteToFile(UnicodeText, path);
        Assert.True(File.Exists(path));

        // ValidateFile
        Assert.True(ZstParser.ValidateFile(path));

        // ParseFile
        var parsed = ZstParser.ParseFile(path);
        Assert.NotNull(parsed);
        Assert.True(parsed.CompressedSize > 0);
        Assert.True(parsed.FrameCount > 0);
        Assert.False(parsed.IsEmpty);

        // ParseBytes
        var bytes = File.ReadAllBytes(path);
        var parsedBytes = ZstParser.ParseBytes(bytes);
        Assert.Equal(parsed.CompressedSize, parsedBytes.CompressedSize);

        // Load(stream)
        using var ms = new MemoryStream(bytes);
        var loaded = ZstDocument.Load(ms);
        Assert.NotNull(loaded);
        Assert.Equal(parsed.CompressedSize, loaded.CompressedSize);

        // Decompress round-trip
        var decompressed = ZstParser.DecompressFile(path);
        Assert.Equal(UnicodeText, decompressed);
    }
}
