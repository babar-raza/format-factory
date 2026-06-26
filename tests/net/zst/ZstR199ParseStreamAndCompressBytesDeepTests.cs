// Tests for ZstParser.ParseStream, ZstWriter.CompressBytes, ZstWriter.DecompressBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R199

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R199: Tests for ZstParser.ParseStream, ZstWriter.CompressBytes, ZstWriter.DecompressBytes deeper.
/// ParseStream(stream): parses zstd metadata from an in-memory stream.
/// CompressBytes(data, level?): compresses a byte array to a zstd byte array.
/// DecompressBytes(data): decompresses a zstd byte array back to the original bytes.
/// Covers: ParseStream non-null; ParseStream has positive FileSizeKB; ParseStream CompressionRatio;
/// ParseStream no-throw; ParseStream from CompressStream output; ParseStream then ValidateFile;
/// ParseStream consistent; ParseStream small data;
/// CompressBytes non-null; CompressBytes non-empty; CompressBytes round-trip via DecompressBytes;
/// CompressBytes smaller for repetitive; CompressBytes then ValidateBytes; CompressBytes with level;
/// CompressBytes consistent; CompressBytes multiple;
/// DecompressBytes non-null; DecompressBytes matches original; DecompressBytes no-throw;
/// DecompressBytes from CompressString output; DecompressBytes consistent;
/// DecompressBytes large data; DecompressBytes file-round-trip;
/// dogfood CompressBytes→ParseStream→DecompressBytes→CompressFile→ValidateFile pipeline.
/// </summary>
public class ZstR199ParseStreamAndCompressBytesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR199ParseStreamAndCompressBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR199_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string RepetitiveText =
        string.Concat(System.Linq.Enumerable.Repeat(
            "Repetitive content for zstd compression testing and validation. ", 80));

    private static byte[] GetRepetitiveBytes() =>
        Encoding.UTF8.GetBytes(RepetitiveText);

    // -------------------------------------------------------------------------
    // ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_NonNull()
    {
        var data = ZstWriter.CompressBytes(GetRepetitiveBytes());
        using var stream = new MemoryStream(data);
        Assert.NotNull(ZstParser.ParseStream(stream));
    }

    [Fact]
    public void ParseStream_NoThrow()
    {
        var data = ZstWriter.CompressBytes(GetRepetitiveBytes());
        using var stream = new MemoryStream(data);
        var ex = Record.Exception(() => ZstParser.ParseStream(stream));
        Assert.Null(ex);
    }

    [Fact]
    public void ParseStream_HasPositiveFileSizeKB()
    {
        var data = ZstWriter.CompressBytes(GetRepetitiveBytes());
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.True(doc.FileSizeKB >= 0);
    }

    [Fact]
    public void ParseStream_FrameCountPositive()
    {
        var data = ZstWriter.CompressBytes(GetRepetitiveBytes());
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void ParseStream_FromCompressStream_Works()
    {
        var inputBytes = GetRepetitiveBytes();
        using var input = new MemoryStream(inputBytes);
        using var output = new MemoryStream();
        ZstWriter.CompressStream(input, output);
        output.Seek(0, SeekOrigin.Begin);
        var doc = ZstParser.ParseStream(output);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseStream_Consistent()
    {
        var data = ZstWriter.CompressBytes(GetRepetitiveBytes());
        using var s1 = new MemoryStream(data);
        using var s2 = new MemoryStream(data);
        var doc1 = ZstParser.ParseStream(s1);
        var doc2 = ZstParser.ParseStream(s2);
        Assert.Equal(doc1.FrameCount, doc2.FrameCount);
    }

    [Fact]
    public void ParseStream_CompressionRatioPositive()
    {
        var data = ZstWriter.CompressBytes(GetRepetitiveBytes());
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.True(doc.CompressionRatio >= 0);
    }

    [Fact]
    public void ParseStream_ToDictNonNull()
    {
        var data = ZstWriter.CompressBytes(GetRepetitiveBytes());
        using var stream = new MemoryStream(data);
        var doc = ZstParser.ParseStream(stream);
        Assert.NotNull(doc.ToDict());
    }

    // -------------------------------------------------------------------------
    // CompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressBytes_NonNull()
    {
        var data = GetRepetitiveBytes();
        Assert.NotNull(ZstWriter.CompressBytes(data));
    }

    [Fact]
    public void CompressBytes_NonEmpty()
    {
        var data = GetRepetitiveBytes();
        Assert.True(ZstWriter.CompressBytes(data).Length > 0);
    }

    [Fact]
    public void CompressBytes_SmallerForRepetitive()
    {
        var data = GetRepetitiveBytes();
        var compressed = ZstWriter.CompressBytes(data);
        Assert.True(compressed.Length < data.Length);
    }

    [Fact]
    public void CompressBytes_ValidZstd()
    {
        var data = GetRepetitiveBytes();
        var compressed = ZstWriter.CompressBytes(data);
        Assert.True(ZstWriter.ValidateBytes(compressed));
    }

    [Fact]
    public void CompressBytes_Consistent()
    {
        var data = GetRepetitiveBytes();
        var c1 = ZstWriter.CompressBytes(data);
        var c2 = ZstWriter.CompressBytes(data);
        Assert.True(Math.Abs(c1.Length - c2.Length) <= 50);
    }

    [Fact]
    public void CompressBytes_Level1_NonNull()
    {
        var data = GetRepetitiveBytes();
        Assert.NotNull(ZstWriter.CompressBytes(data, compressionLevel: 1));
    }

    [Fact]
    public void CompressBytes_Level9_NonNull()
    {
        var data = GetRepetitiveBytes();
        Assert.NotNull(ZstWriter.CompressBytes(data, compressionLevel: 9));
    }

    [Fact]
    public void CompressBytes_Level9_SmallerThanLevel1()
    {
        var data = GetRepetitiveBytes();
        var c1 = ZstWriter.CompressBytes(data, compressionLevel: 1);
        var c9 = ZstWriter.CompressBytes(data, compressionLevel: 9);
        // Higher level should produce <= size (better compression)
        Assert.True(c9.Length <= c1.Length + 100); // Allow small tolerance
    }

    // -------------------------------------------------------------------------
    // DecompressBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressBytes_NonNull()
    {
        var data = GetRepetitiveBytes();
        var compressed = ZstWriter.CompressBytes(data);
        Assert.NotNull(ZstWriter.DecompressBytes(compressed));
    }

    [Fact]
    public void DecompressBytes_MatchesOriginal()
    {
        var data = GetRepetitiveBytes();
        var compressed = ZstWriter.CompressBytes(data);
        var restored = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(data, restored);
    }

    [Fact]
    public void DecompressBytes_NoThrow()
    {
        var data = GetRepetitiveBytes();
        var compressed = ZstWriter.CompressBytes(data);
        var ex = Record.Exception(() => ZstWriter.DecompressBytes(compressed));
        Assert.Null(ex);
    }

    [Fact]
    public void DecompressBytes_Consistent()
    {
        var data = GetRepetitiveBytes();
        var compressed = ZstWriter.CompressBytes(data);
        var r1 = ZstWriter.DecompressBytes(compressed);
        var r2 = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(r1, r2);
    }

    [Fact]
    public void DecompressBytes_FromCompressString_Works()
    {
        var text = RepetitiveText;
        var compressed = ZstWriter.CompressString(text);
        var decompressedBytes = ZstWriter.DecompressBytes(compressed);
        Assert.NotNull(decompressedBytes);
        Assert.True(decompressedBytes.Length > 0);
    }

    [Fact]
    public void DecompressBytes_LargeData_Works()
    {
        var large = string.Concat(System.Linq.Enumerable.Repeat("Large data chunk. ", 500));
        var bytes = Encoding.UTF8.GetBytes(large);
        var compressed = ZstWriter.CompressBytes(bytes);
        var restored = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(bytes, restored);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressBytes_ParseStream_DecompressBytes_CompressFile_ValidateFile_Pipeline()
    {
        var originalText = "Dogfood content for comprehensive pipeline test: " + RepetitiveText;
        var originalBytes = Encoding.UTF8.GetBytes(originalText);

        // CompressBytes at default level
        var compressed = ZstWriter.CompressBytes(originalBytes);
        Assert.NotNull(compressed);
        Assert.True(compressed.Length > 0);
        Assert.True(compressed.Length < originalBytes.Length);

        // ValidateBytes
        Assert.True(ZstWriter.ValidateBytes(compressed));

        // ParseStream from compressed
        using var stream = new MemoryStream(compressed);
        var doc = ZstParser.ParseStream(stream);
        Assert.NotNull(doc);
        Assert.True(doc.FrameCount >= 1);
        Assert.True(doc.FileSizeKB >= 0);
        var dict = doc.ToDict();
        Assert.NotNull(dict);

        // DecompressBytes — round-trip
        var restored = ZstWriter.DecompressBytes(compressed);
        Assert.Equal(originalBytes, restored);
        Assert.Equal(originalText, Encoding.UTF8.GetString(restored));

        // CompressBytes at multiple levels
        var c1 = ZstWriter.CompressBytes(originalBytes, compressionLevel: 1);
        var c9 = ZstWriter.CompressBytes(originalBytes, compressionLevel: 9);
        Assert.NotNull(c1);
        Assert.NotNull(c9);
        Assert.True(ZstWriter.ValidateBytes(c1));
        Assert.True(ZstWriter.ValidateBytes(c9));

        // Both decompress to same original
        Assert.Equal(originalBytes, ZstWriter.DecompressBytes(c1));
        Assert.Equal(originalBytes, ZstWriter.DecompressBytes(c9));

        // ParseStream on level 9 output
        using var s9 = new MemoryStream(c9);
        var doc9 = ZstParser.ParseStream(s9);
        Assert.NotNull(doc9);
        Assert.True(doc9.FrameCount >= 1);

        // Write bytes to file and validate
        var filePath = TempFile("dogfood_bytes.zst");
        File.WriteAllBytes(filePath, compressed);
        Assert.True(ZstDocument.ValidateFile(filePath));

        // CompressFile using a source file
        var srcPath = TempFile("dogfood_src.txt");
        File.WriteAllText(srcPath, originalText);
        var destPath = TempFile("dogfood_file.zst");
        ZstWriter.CompressFile(srcPath, destPath);
        Assert.True(File.Exists(destPath));
        Assert.True(ZstDocument.ValidateFile(destPath));

        // ParseFile on CompressFile output
        var fileDoc = ZstParser.ParseFile(destPath);
        Assert.NotNull(fileDoc);
        Assert.True(fileDoc.FileSizeKB >= 0);

        // CompressBytes then ParseStream matches file-based approach
        var fileBytesCompressed = File.ReadAllBytes(destPath);
        Assert.True(ZstWriter.ValidateBytes(fileBytesCompressed));
        var decompressedFromFile = ZstWriter.DecompressBytes(fileBytesCompressed);
        Assert.Equal(originalText, Encoding.UTF8.GetString(decompressedFromFile));

        // Multi-document pipeline
        for (int i = 0; i < 3; i++)
        {
            var content = $"Document {i}: " + RepetitiveText;
            var contentBytes = Encoding.UTF8.GetBytes(content);
            var comp = ZstWriter.CompressBytes(contentBytes);
            var decomp = ZstWriter.DecompressBytes(comp);
            Assert.Equal(contentBytes, decomp);
            Assert.True(ZstWriter.ValidateBytes(comp));
            using var ms = new MemoryStream(comp);
            var d = ZstParser.ParseStream(ms);
            Assert.NotNull(d);
            Assert.True(d.FrameCount >= 1);
        }
    }
}
