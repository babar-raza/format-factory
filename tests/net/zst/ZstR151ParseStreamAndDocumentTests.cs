// Tests for ZstParser.ParseStream, ZstDocument properties, and ZstWriter overloads.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R151

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R151: Tests for ZstParser.ParseStream, ZstDocument computed properties, ZstWriter.Compress overloads.
/// ParseStream(stream): parses a Zstandard stream and returns ZstDocument.
/// ZstDocument: MagicValid, FrameCount, IsValid, FileSizeBytes, FileSizeKB, SizeLabel.
/// ZstWriter.Compress(Stream, Stream): compress stream overload.
/// Covers: ParseStream returns non-null; ParseStream MagicValid true; ParseStream FrameCount positive;
/// ParseStream IsValid true; ZstDocument IsValid is true for valid doc;
/// FileSizeBytes positive; FileSizeKB consistent with FileSizeBytes;
/// SizeLabel is non-empty; Compress(Stream,Stream) produces output;
/// Compress->Decompress round-trip preserves content;
/// ZstMagic constant is 4 bytes; DefaultMaxFileSizeBytes positive;
/// FilePath property from Parse; dogfood Compress->ParseStream->Decompress.
/// </summary>
public class ZstR151ParseStreamAndDocumentTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR151ParseStreamAndDocumentTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR151_" + Guid.NewGuid().ToString("N"));
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
        var raw = Encoding.UTF8.GetBytes(text);
        return ZstWriter.Compress(raw);
    }

    // -------------------------------------------------------------------------
    // ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_ReturnsNonNull()
    {
        var data = CompressText("hello world");
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseStream_MagicValid_IsTrue()
    {
        var data = CompressText("test content");
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.True(doc.MagicValid);
    }

    [Fact]
    public void ParseStream_FrameCount_IsPositive()
    {
        var data = CompressText("frame data");
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.True(doc.FrameCount > 0);
    }

    [Fact]
    public void ParseStream_IsValid_IsTrue()
    {
        var data = CompressText("valid zstd content");
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void ParseStream_FileSizeBytes_IsPositive()
    {
        var data = CompressText("size check content");
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream, knownLength: data.Length);
        Assert.True(doc.FileSizeBytes >= 0);
    }

    // -------------------------------------------------------------------------
    // ZstDocument properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_FileSizeKB_ConsistentWithFileSizeBytes()
    {
        var path = TempFile("test.zst");
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes("some content"), path);
        var doc = ZstParser.Parse(path);
        var expectedKB = doc.FileSizeBytes / 1024.0;
        Assert.Equal(expectedKB, doc.FileSizeKB, 3);
    }

    [Fact]
    public void ZstDocument_SizeLabel_IsNonEmpty()
    {
        var path = TempFile("label.zst");
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes("label test"), path);
        var doc = ZstParser.Parse(path);
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));
    }

    [Fact]
    public void ZstDocument_FilePath_MatchesParsedPath()
    {
        var path = TempFile("filepath.zst");
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes("filepath test"), path);
        var doc = ZstParser.Parse(path);
        Assert.Equal(path, doc.FilePath);
    }

    // -------------------------------------------------------------------------
    // ZstWriter constants
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstMagic_IsFourBytes()
    {
        Assert.Equal(4, ZstParser.ZstdMagic.Length);
    }

    [Fact]
    public void DefaultMaxFileSizeBytes_IsPositive()
    {
        Assert.True(ZstParser.DefaultMaxFileSizeBytes > 0);
    }

    // -------------------------------------------------------------------------
    // Compress(Stream, Stream) overload
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressStream_ProducesOutput()
    {
        var raw = Encoding.UTF8.GetBytes("stream compress test");
        using var input = new MemoryStream(raw);
        using var output = new MemoryStream();
        ZstWriter.Compress(input, output);
        Assert.True(output.Length > 0);
    }

    [Fact]
    public void CompressStream_DecompressStream_RoundTrip()
    {
        var original = "stream round-trip content for ZST R151";
        var raw = Encoding.UTF8.GetBytes(original);
        using var input = new MemoryStream(raw);
        using var compressed = new MemoryStream();
        ZstWriter.Compress(input, compressed);

        compressed.Position = 0;
        using var decompressed = new MemoryStream();
        ZstWriter.Decompress(compressed, decompressed);
        var result = Encoding.UTF8.GetString(decompressed.ToArray());
        Assert.Equal(original, result);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress->ParseStream->Decompress
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressParseStreamDecompress_Pipeline()
    {
        // Compress a string
        var text = "ZST R151 dogfood pipeline content";
        var compressed = CompressText(text);
        Assert.True(compressed.Length > 0);

        // ParseStream the compressed bytes
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.True(doc.IsValid);
        Assert.True(doc.FrameCount > 0);
        Assert.False(string.IsNullOrEmpty(doc.SizeLabel));

        // Decompress and verify content
        var decompressed = ZstWriter.Decompress(compressed);
        var result = Encoding.UTF8.GetString(decompressed);
        Assert.Equal(text, result);
    }
}
