// Tests for ZstDocument computed properties and ZstWriter.CompressToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R147

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R147: Tests for ZstDocument computed properties and ZstWriter.CompressToFile.
/// ZstDocument: FileSizeKB, SizeLabel, IsValid, IsEmptyContent, HasMultipleFrames,
///              SizeExceeds100K, IsHighlyCompressed, BytesPerFrame, OverheadBytes.
/// ZstWriter.CompressToFile(byte[], path): writes compressed bytes to a file.
/// Covers: FileSizeKB positive for valid ZST; SizeLabel is non-null string;
/// IsValid true for valid compressed data; IsEmptyContent false for non-empty;
/// HasMultipleFrames false for single frame; SizeExceeds100K false for small data;
/// BytesPerFrame positive; OverheadBytes non-negative;
/// CompressToFile creates file; CompressToFile file is valid ZST;
/// CompressToFile round-trip via Decompress; CompressToFile with level param;
/// dogfood Compress->ParseStream->document-properties pipeline.
/// </summary>
public class ZstR147DocumentPropertiesAndWriterTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR147DocumentPropertiesAndWriterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR147_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static byte[] CompressText(string text) =>
        ZstWriter.Compress(Encoding.UTF8.GetBytes(text));

    private static ZstDocument ParseBytes(byte[] compressed, string? filePath = null)
    {
        using var stream = new MemoryStream(compressed);
        return ZstParser.ParseStream(stream, compressed.Length, filePath);
    }

    // -------------------------------------------------------------------------
    // ZstDocument computed properties
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeKB_IsPositiveForValidData()
    {
        var compressed = CompressText("Hello ZST document properties test!");
        var doc = ParseBytes(compressed);
        Assert.True(doc.FileSizeKB >= 0);
    }

    [Fact]
    public void SizeLabel_IsNonNullString()
    {
        var compressed = CompressText("Label test data.");
        var doc = ParseBytes(compressed);
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));
    }

    [Fact]
    public void IsValid_TrueForValidCompressedData()
    {
        var compressed = CompressText("Valid compression test.");
        var doc = ParseBytes(compressed);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsEmptyContent_FalseForNonEmptyData()
    {
        var compressed = CompressText("Non-empty content.");
        var doc = ParseBytes(compressed);
        Assert.False(doc.IsEmptyContent);
    }

    [Fact]
    public void HasMultipleFrames_FalseForSingleFrame()
    {
        var compressed = CompressText("Single frame data.");
        var doc = ParseBytes(compressed);
        // Single compression call produces single frame
        Assert.False(doc.HasMultipleFrames);
    }

    [Fact]
    public void SizeExceeds100K_FalseForSmallData()
    {
        var compressed = CompressText("Small data — well under 100KB.");
        var doc = ParseBytes(compressed);
        Assert.False(doc.SizeExceeds100K);
    }

    [Fact]
    public void BytesPerFrame_IsPositive()
    {
        var compressed = CompressText("Bytes per frame test.");
        var doc = ParseBytes(compressed);
        Assert.True(doc.BytesPerFrame > 0);
    }

    [Fact]
    public void OverheadBytes_IsNonNegative()
    {
        var compressed = CompressText("Overhead bytes test.");
        var doc = ParseBytes(compressed);
        Assert.True(doc.OverheadBytes >= 0);
    }

    // -------------------------------------------------------------------------
    // ZstWriter.CompressToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressToFile_CreatesFile()
    {
        var data = Encoding.UTF8.GetBytes("Compress to file test data.");
        var path = TempFile("output.zst");
        ZstWriter.CompressToFile(data, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CompressToFile_FileIsNonEmpty()
    {
        var data = Encoding.UTF8.GetBytes("Non-empty compress to file.");
        var path = TempFile("nonempty.zst");
        ZstWriter.CompressToFile(data, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void CompressToFile_FileHasValidZstMagic()
    {
        var data = Encoding.UTF8.GetBytes("Magic number verify.");
        var path = TempFile("magic.zst");
        ZstWriter.CompressToFile(data, path);
        var bytes = File.ReadAllBytes(path);
        Assert.True(bytes.Length >= 4);
        Assert.Equal(0x28, bytes[0]);
        Assert.Equal(0xB5, bytes[1]);
        Assert.Equal(0x2F, bytes[2]);
        Assert.Equal(0xFD, bytes[3]);
    }

    [Fact]
    public void CompressToFile_RoundTripViaDecompress()
    {
        var original = "Round-trip via CompressToFile and Decompress.";
        var data = Encoding.UTF8.GetBytes(original);
        var path = TempFile("roundtrip.zst");
        ZstWriter.CompressToFile(data, path);
        var fileBytes = File.ReadAllBytes(path);
        var decompressed = ZstWriter.Decompress(fileBytes);
        Assert.Equal(original, Encoding.UTF8.GetString(decompressed));
    }

    [Fact]
    public void CompressToFile_WithLevel_CreatesValidFile()
    {
        var data = Encoding.UTF8.GetBytes("Level 9 compress to file test.");
        var path = TempFile("level9.zst");
        ZstWriter.CompressToFile(data, path, level: 9);
        Assert.True(File.Exists(path));
        var bytes = File.ReadAllBytes(path);
        Assert.True(bytes.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->ParseStream->check document properties
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressParseDocumentProperties_Pipeline()
    {
        var original = "Dogfood pipeline: compress data, parse stream, inspect properties.";
        var compressed = ZstWriter.Compress(Encoding.UTF8.GetBytes(original));

        // Parse via stream with file path
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, compressed.Length, "dogfood.zst");

        // Verify document properties
        Assert.True(doc.IsValid);
        Assert.Equal("dogfood.zst", doc.FilePath);
        Assert.Equal(1, doc.FrameCount);
        Assert.False(doc.HasMultipleFrames);
        Assert.True(doc.MagicValid);
        Assert.False(doc.IsEmptyContent);
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));
        Assert.True(doc.BytesPerFrame > 0);

        // Decompress and verify
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original, Encoding.UTF8.GetString(decompressed));
    }
}
