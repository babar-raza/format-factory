// Tests for ZstParser.ParseStream and ZstWriter.Decompress (stream overloads).
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R156

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R156: Tests for ZstParser.ParseStream, ZstWriter.Decompress stream overload, byte round-trips.
/// ParseStream(stream): parses a ZST document from a stream.
/// ZstWriter.Decompress(compressedBytes): decompresses bytes.
/// ZstWriter.Compress(inputBytes, level): compresses bytes in memory.
/// Covers: ParseStream from MemoryStream is valid; ParseStream MagicValid is true;
/// ParseStream FrameCount is 1; ParseStream FileSizeBytes equals stream length;
/// Decompress(Compress(bytes)) round-trips content;
/// Compress returns non-empty bytes; Compress then Decompress is equal to original;
/// Decompress small content; Compress->Decompress UTF8 text;
/// ParseStream after Compress and write to MemoryStream;
/// ZstDocument.IsValid after ParseStream; SizeLabel non-null after ParseStream;
/// Compress level=1 output is non-empty; Compress level=22 output is non-empty;
/// dogfood Compress->MemoryStream->ParseStream->Decompress verify pipeline.
/// </summary>
public class ZstR156ParseStreamAndDecompressTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR156ParseStreamAndDecompressTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR156_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static byte[] CompressAndGetBytes(string text, int level = 3)
    {
        var path = Path.Combine(Path.GetTempPath(), "zst_temp_" + Guid.NewGuid().ToString("N") + ".zst");
        try
        {
            ZstWriter.CompressToFile(Encoding.UTF8.GetBytes(text), path, level);
            return File.ReadAllBytes(path);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    // -------------------------------------------------------------------------
    // ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_FromMemoryStream_IsValid()
    {
        var compressed = CompressAndGetBytes("Hello ZST R156 stream test.");
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void ParseStream_MagicValid_IsTrue()
    {
        var compressed = CompressAndGetBytes("Magic valid test content.");
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void ParseStream_FrameCount_IsOne()
    {
        var compressed = CompressAndGetBytes("Single frame content.");
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.Equal(1, doc.FrameCount);
    }

    [Fact]
    public void ParseStream_FileSizeBytes_EqualsStreamLength()
    {
        var compressed = CompressAndGetBytes("File size bytes test.");
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.Equal(compressed.Length, doc.FileSizeBytes);
    }

    [Fact]
    public void ParseStream_IsValid_AfterCompress()
    {
        var compressed = CompressAndGetBytes("Validity check content.");
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.MagicValid && doc.FrameCount > 0);
    }

    [Fact]
    public void ParseStream_SizeLabel_NonNull()
    {
        var compressed = CompressAndGetBytes("Size label test content.");
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.NotNull(doc.SizeLabel);
    }

    // -------------------------------------------------------------------------
    // Compress / Decompress in memory
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_ReturnsNonEmptyBytes()
    {
        var input = Encoding.UTF8.GetBytes("Compress test content.");
        var compressed = ZstWriter.Compress(input);
        Assert.NotEmpty(compressed);
    }

    [Fact]
    public void Compress_Then_Decompress_RoundTripsContent()
    {
        var original = "Round-trip ZST content test.";
        var input = Encoding.UTF8.GetBytes(original);
        var compressed = ZstWriter.Compress(input);
        var decompressed = ZstWriter.Decompress(compressed);
        var result = Encoding.UTF8.GetString(decompressed);
        Assert.Equal(original, result);
    }

    [Fact]
    public void Compress_Level1_OutputNonEmpty()
    {
        var input = Encoding.UTF8.GetBytes("Level 1 compression test.");
        var compressed = ZstWriter.Compress(input, level: 1);
        Assert.NotEmpty(compressed);
    }

    [Fact]
    public void Compress_Level22_OutputNonEmpty()
    {
        var input = Encoding.UTF8.GetBytes("Level 22 compression test.");
        var compressed = ZstWriter.Compress(input, level: 22);
        Assert.NotEmpty(compressed);
    }

    [Fact]
    public void Decompress_SmallContent_ReturnsBytes()
    {
        var input = Encoding.UTF8.GetBytes("tiny");
        var compressed = ZstWriter.Compress(input);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.NotEmpty(decompressed);
    }

    [Fact]
    public void Compress_Decompress_UTF8Text_Equal()
    {
        var text = "Hello, UTF-8 world! Special: αβγδ";
        var input = Encoding.UTF8.GetBytes(text);
        var compressed = ZstWriter.Compress(input);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(text, Encoding.UTF8.GetString(decompressed));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->MemoryStream->ParseStream->Decompress verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressMemoryStreamParseStreamDecompress_Pipeline()
    {
        var originalText = "R156 dogfood: compress to bytes, parse from stream, decompress and verify.";
        var originalBytes = Encoding.UTF8.GetBytes(originalText);

        // Compress
        var compressed = ZstWriter.Compress(originalBytes);
        Assert.NotEmpty(compressed);

        // ParseStream
        using var ms = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.IsValid);
        Assert.True(doc.MagicValid);
        Assert.Equal(1, doc.FrameCount);
        Assert.Equal(compressed.Length, doc.FileSizeBytes);
        Assert.NotNull(doc.ContentTypeHint);
        Assert.NotNull(doc.SizeLabel);

        // Decompress and verify content
        var decompressed = ZstWriter.Decompress(compressed);
        var resultText = Encoding.UTF8.GetString(decompressed);
        Assert.Equal(originalText, resultText);
    }
}
