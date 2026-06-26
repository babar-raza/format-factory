// Tests for ZstWriter.Decompress overloads and ZstDocument content hint properties.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R143

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R143: Tests for ZstWriter.Decompress overloads and ZstDocument content hint properties.
/// ZstWriter.Decompress(byte[], long): decompresses byte array; throws if too large.
/// ZstWriter.Decompress(Stream, Stream, long): decompresses from stream to stream.
/// ZstDocument.ContentTypeHint: "unknown" for generic content.
/// ZstDocument.IsEmptyContent: true when decompressed size is 0.
/// ZstDocument.HasMultipleFrames: true when FrameCount > 1.
/// ZstDocument.FileSizeKB: FileSizeBytes / 1024.0.
/// ZstDocument.IsValid: MagicValid and FrameCount > 0.
/// Covers: Decompress byte[] round-trip; Decompress stream round-trip;
/// Decompress limit exceeded throws; ContentTypeHint default is unknown;
/// IsEmptyContent false for non-empty; HasMultipleFrames false for single frame;
/// FileSizeKB proportional to size; IsValid true for valid zst;
/// IsValid false for invalid bytes; dogfood Compress->Parse->Decompress->verify pipeline.
/// </summary>
public class ZstR143DecompressAndContentHintTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR143DecompressAndContentHintTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR143_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static byte[] CompressText(string text)
    {
        var bytes = System.Text.Encoding.UTF8.GetBytes(text);
        return ZstWriter.Compress(bytes);
    }

    // -------------------------------------------------------------------------
    // Decompress(byte[])
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_ByteArray_RoundTrip()
    {
        var original = "Hello, ZST world!";
        var compressed = CompressText(original);
        var decompressed = ZstWriter.Decompress(compressed);
        var result = System.Text.Encoding.UTF8.GetString(decompressed);
        Assert.Equal(original, result);
    }

    [Fact]
    public void Decompress_ByteArray_LargeData_RoundTrip()
    {
        var original = new string('A', 10_000);
        var compressed = CompressText(original);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(original.Length, System.Text.Encoding.UTF8.GetCharCount(decompressed));
    }

    [Fact]
    public void Decompress_ByteArray_EmptySource_ReturnsEmpty()
    {
        var original = "";
        var compressed = CompressText(original);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Empty(decompressed);
    }

    [Fact]
    public void Decompress_ByteArray_LimitExceeded_Throws()
    {
        var original = new string('B', 1000);
        var compressed = CompressText(original);
        // Set limit far below actual decompressed size
        Assert.ThrowsAny<Exception>(() => ZstWriter.Decompress(compressed, maxDecompressedBytes: 10));
    }

    // -------------------------------------------------------------------------
    // Decompress(Stream, Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void Decompress_Stream_RoundTrip()
    {
        var original = "Stream round-trip test!";
        var originalBytes = System.Text.Encoding.UTF8.GetBytes(original);
        var compressed = ZstWriter.Compress(originalBytes);

        using var inputStream = new MemoryStream(compressed);
        using var outputStream = new MemoryStream();
        ZstWriter.Decompress(inputStream, outputStream);

        var result = System.Text.Encoding.UTF8.GetString(outputStream.ToArray());
        Assert.Equal(original, result);
    }

    [Fact]
    public void Decompress_Stream_WritesToOutput()
    {
        var data = System.Text.Encoding.UTF8.GetBytes("stream test data");
        var compressed = ZstWriter.Compress(data);

        using var inputStream = new MemoryStream(compressed);
        using var outputStream = new MemoryStream();
        ZstWriter.Decompress(inputStream, outputStream);

        Assert.True(outputStream.Length > 0);
    }

    // -------------------------------------------------------------------------
    // ZstDocument properties: ContentTypeHint, IsEmptyContent, HasMultipleFrames, FileSizeKB, IsValid
    // -------------------------------------------------------------------------

    [Fact]
    public void ContentTypeHint_Default_IsUnknown()
    {
        var path = TempFile("hint.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("data"), path);
        var doc = ZstParser.Parse(path);
        Assert.Equal("unknown", doc.ContentTypeHint);
    }

    [Fact]
    public void IsEmptyContent_NonEmpty_IsFalse()
    {
        var path = TempFile("nonempty.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("content"), path);
        var doc = ZstParser.Parse(path);
        Assert.False(doc.IsEmptyContent);
    }

    [Fact]
    public void HasMultipleFrames_SingleFrame_IsFalse()
    {
        var path = TempFile("single.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("single frame"), path);
        var doc = ZstParser.Parse(path);
        Assert.False(doc.HasMultipleFrames);
    }

    [Fact]
    public void FileSizeKB_IsProportional()
    {
        var path = TempFile("size.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("test data for size"), path);
        var doc = ZstParser.Parse(path);
        var expectedKB = doc.FileSizeBytes / 1024.0;
        Assert.Equal(expectedKB, doc.FileSizeKB, precision: 5);
    }

    [Fact]
    public void IsValid_ValidZst_IsTrue()
    {
        var path = TempFile("valid.zst");
        ZstWriter.CompressToFile(System.Text.Encoding.UTF8.GetBytes("valid content"), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_InvalidBytes_IsFalse()
    {
        var invalidBytes = new byte[] { 0x00, 0x01, 0x02, 0x03 };
        using var stream = new MemoryStream(invalidBytes);
        var doc = ZstParser.ParseStream(stream, knownLength: invalidBytes.Length);
        Assert.False(doc.IsValid);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->CompressToFile->Parse->Decompress->verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressParseDecompress_Pipeline()
    {
        var original = "Dogfood pipeline: compress, parse, decompress, verify.";
        var originalBytes = System.Text.Encoding.UTF8.GetBytes(original);

        // Compress to file
        var path = TempFile("pipeline.zst");
        ZstWriter.CompressToFile(originalBytes, path);

        // Parse
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
        Assert.False(doc.IsEmptyContent);
        Assert.Equal("unknown", doc.ContentTypeHint);
        Assert.True(doc.FileSizeKB > 0);

        // Decompress (round-trip via byte array)
        var compressed = File.ReadAllBytes(path);
        var decompressed = ZstWriter.Decompress(compressed);
        var result = System.Text.Encoding.UTF8.GetString(decompressed);
        Assert.Equal(original, result);
    }
}
