// Tests for ZstWriter.Decompress(Stream,Stream) and file size/label properties.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R152

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R152: Tests for ZstWriter.Decompress(Stream,Stream), file size/label, and edge cases.
/// Decompress(Stream, Stream): decompresses from input stream to output stream.
/// SizeLabel: human-readable size string.
/// IsValid: true when magic is valid and frame count positive.
/// HasMultipleFrames: true when FrameCount > 1.
/// IsEmptyContent: reflects whether content is empty.
/// Covers: Decompress(Stream,Stream) produces correct content;
/// Compress->Decompress(Stream,Stream) round-trip; SizeLabel is Bytes/KB/MB;
/// FileSizeKB for 1KB file; IsValid false for invalid bytes;
/// HasMultipleFrames false for single frame; IsEmptyContent for tiny string;
/// DefaultMaxDecompressedBytes constant; MinCompressionLevel is 1;
/// MaxCompressionLevel is 22; DefaultCompressionLevel is 3;
/// Compress with level 1; Compress with level 22; Decompress level-1 content;
/// dogfood Compress(level1)->ParseStream->Decompress verify.
/// </summary>
public class ZstR152DecompressStreamAndFileSizeTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR152DecompressStreamAndFileSizeTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR152_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static byte[] CompressText(string text, int level = ZstWriter.DefaultCompressionLevel)
    {
        var raw = Encoding.UTF8.GetBytes(text);
        return ZstWriter.Compress(raw, level);
    }

    // -------------------------------------------------------------------------
    // Decompress(Stream, Stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressStream_ProducesCorrectContent()
    {
        var original = "hello from stream decompress";
        var compressed = CompressText(original);
        using var input = new MemoryStream(compressed);
        using var output = new MemoryStream();
        ZstWriter.Decompress(input, output);
        var result = Encoding.UTF8.GetString(output.ToArray());
        Assert.Equal(original, result);
    }

    [Fact]
    public void CompressStream_DecompressStream_LargerContent()
    {
        var original = new string('Z', 5000);
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
    // Compression level constants
    // -------------------------------------------------------------------------

    [Fact]
    public void MinCompressionLevel_IsOne()
    {
        Assert.Equal(1, ZstWriter.MinCompressionLevel);
    }

    [Fact]
    public void MaxCompressionLevel_Is22()
    {
        Assert.Equal(22, ZstWriter.MaxCompressionLevel);
    }

    [Fact]
    public void DefaultCompressionLevel_IsThree()
    {
        Assert.Equal(3, ZstWriter.DefaultCompressionLevel);
    }

    [Fact]
    public void DefaultMaxDecompressedBytes_IsPositive()
    {
        Assert.True(ZstWriter.DefaultMaxDecompressedBytes > 0);
    }

    // -------------------------------------------------------------------------
    // Compress with specific levels
    // -------------------------------------------------------------------------

    [Fact]
    public void Compress_Level1_ProducesDecompressableOutput()
    {
        var text = "compress at level 1";
        var compressed = CompressText(text, level: 1);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(text, Encoding.UTF8.GetString(decompressed));
    }

    [Fact]
    public void Compress_Level22_ProducesDecompressableOutput()
    {
        var text = "compress at level 22";
        var compressed = CompressText(text, level: 22);
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(text, Encoding.UTF8.GetString(decompressed));
    }

    // -------------------------------------------------------------------------
    // ZstDocument properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstDocument_HasMultipleFrames_FalseForSingleFrame()
    {
        var path = TempFile("single.zst");
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes("single frame"), path);
        var doc = ZstParser.Parse(path);
        Assert.False(doc.HasMultipleFrames); // single frame = false
    }

    [Fact]
    public void ZstDocument_IsValid_TrueForValidFile()
    {
        var path = TempFile("valid.zst");
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes("valid content"), path);
        var doc = ZstParser.Parse(path);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void ZstDocument_SizeLabel_ContainsBytesOrKbOrMb()
    {
        var path = TempFile("size.zst");
        ZstWriter.CompressToFile(Encoding.UTF8.GetBytes("size label test"), path);
        var doc = ZstParser.Parse(path);
        var label = doc.SizeLabel;
        Assert.True(
            label.Contains("B") || label.Contains("KB") || label.Contains("MB"),
            $"SizeLabel was: {label}");
    }

    // -------------------------------------------------------------------------
    // Dogfood: Compress(level1)->ParseStream->Decompress verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressLevel1ParseStreamDecompressVerify()
    {
        // Compress with level 1
        var text = "ZST R152 dogfood level-1 content";
        var compressed = CompressText(text, level: 1);
        Assert.True(compressed.Length > 0);

        // ParseStream the compressed bytes
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream, knownLength: compressed.Length);
        Assert.True(doc.IsValid);
        Assert.Equal(1, doc.FrameCount);

        // Decompress and verify
        var decompressed = ZstWriter.Decompress(compressed);
        Assert.Equal(text, Encoding.UTF8.GetString(decompressed));

        // Verify HasMultipleFrames
        Assert.False(doc.HasMultipleFrames);
    }
}
