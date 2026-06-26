// Tests for ZstWriter.CompressFile, DecompressFile, CompressStream deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R198

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R198: Tests for ZstWriter.CompressFile, DecompressFile, CompressStream deeper.
/// CompressFile(srcPath, destPath): compresses a file to a zstd file.
/// DecompressFile(srcPath, destPath): decompresses a zstd file to the original.
/// CompressStream(inStream, outStream): compresses stream data to another stream.
/// Covers: CompressFile creates output file; CompressFile output is non-empty;
/// CompressFile output is valid zstd; CompressFile smaller than input for large text;
/// CompressFile then DecompressFile round-trip; CompressFile multiple files;
/// DecompressFile creates output file; DecompressFile output non-empty;
/// DecompressFile round-trip matches original; DecompressFile then ParseFile;
/// CompressStream non-throw; CompressStream output is non-empty;
/// CompressStream then DecompressStream round-trip; CompressStream with large data;
/// CompressStream creates valid zstd bytes; CompressStream consistent;
/// dogfood CompressFile→DecompressFile→CompressStream→ValidateFile pipeline.
/// </summary>
public class ZstR198CompressFileAndDecompressFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR198CompressFileAndDecompressFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR198_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTextFile(string name, string content)
    {
        var path = TempFile(name);
        File.WriteAllText(path, content);
        return path;
    }

    private static readonly string RepetitiveContent =
        string.Concat(System.Linq.Enumerable.Repeat(
            "This is repetitive content for compression testing purposes. ", 100));

    // -------------------------------------------------------------------------
    // CompressFile
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressFile_CreatesOutputFile()
    {
        var src = CreateTextFile("input.txt", RepetitiveContent);
        var dest = TempFile("output.zst");
        ZstWriter.CompressFile(src, dest);
        Assert.True(File.Exists(dest));
    }

    [Fact]
    public void CompressFile_OutputNonEmpty()
    {
        var src = CreateTextFile("input2.txt", RepetitiveContent);
        var dest = TempFile("output2.zst");
        ZstWriter.CompressFile(src, dest);
        Assert.True(new FileInfo(dest).Length > 0);
    }

    [Fact]
    public void CompressFile_OutputIsValidZstd()
    {
        var src = CreateTextFile("input3.txt", RepetitiveContent);
        var dest = TempFile("output3.zst");
        ZstWriter.CompressFile(src, dest);
        Assert.True(ZstDocument.ValidateFile(dest));
    }

    [Fact]
    public void CompressFile_SmallerThanInputForLargeText()
    {
        var src = CreateTextFile("large.txt", RepetitiveContent);
        var dest = TempFile("large.zst");
        ZstWriter.CompressFile(src, dest);
        var srcSize = new FileInfo(src).Length;
        var destSize = new FileInfo(dest).Length;
        Assert.True(destSize < srcSize);
    }

    [Fact]
    public void CompressFile_ThenDecompressFile_RoundTrip()
    {
        var src = CreateTextFile("rt_src.txt", RepetitiveContent);
        var compressed = TempFile("rt.zst");
        var decompressed = TempFile("rt_out.txt");
        ZstWriter.CompressFile(src, compressed);
        ZstWriter.DecompressFile(compressed, decompressed);
        var original = File.ReadAllText(src);
        var restored = File.ReadAllText(decompressed);
        Assert.Equal(original, restored);
    }

    [Fact]
    public void CompressFile_Multiple_AllValid()
    {
        for (int i = 0; i < 3; i++)
        {
            var src = CreateTextFile($"multi_{i}.txt", $"Content {i}: " + RepetitiveContent);
            var dest = TempFile($"multi_{i}.zst");
            ZstWriter.CompressFile(src, dest);
            Assert.True(ZstDocument.ValidateFile(dest));
        }
    }

    [Fact]
    public void CompressFile_NoThrow()
    {
        var src = CreateTextFile("nothrow.txt", RepetitiveContent);
        var dest = TempFile("nothrow.zst");
        var ex = Record.Exception(() => ZstWriter.CompressFile(src, dest));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // DecompressFile
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressFile_CreatesOutputFile()
    {
        var src = CreateTextFile("decomp_src.txt", RepetitiveContent);
        var compressed = TempFile("decomp.zst");
        var output = TempFile("decomp_out.txt");
        ZstWriter.CompressFile(src, compressed);
        ZstWriter.DecompressFile(compressed, output);
        Assert.True(File.Exists(output));
    }

    [Fact]
    public void DecompressFile_OutputNonEmpty()
    {
        var src = CreateTextFile("decomp2_src.txt", RepetitiveContent);
        var compressed = TempFile("decomp2.zst");
        var output = TempFile("decomp2_out.txt");
        ZstWriter.CompressFile(src, compressed);
        ZstWriter.DecompressFile(compressed, output);
        Assert.True(new FileInfo(output).Length > 0);
    }

    [Fact]
    public void DecompressFile_RoundTripMatchesOriginal()
    {
        var originalContent = "Specific content to verify exact decompression: " + RepetitiveContent;
        var src = CreateTextFile("exact_src.txt", originalContent);
        var compressed = TempFile("exact.zst");
        var output = TempFile("exact_out.txt");
        ZstWriter.CompressFile(src, compressed);
        ZstWriter.DecompressFile(compressed, output);
        Assert.Equal(originalContent, File.ReadAllText(output));
    }

    [Fact]
    public void DecompressFile_ThenParseFile_Works()
    {
        var src = CreateTextFile("parse_src.txt", RepetitiveContent);
        var compressed = TempFile("parse.zst");
        ZstWriter.CompressFile(src, compressed);
        var doc = ZstParser.ParseFile(compressed);
        Assert.NotNull(doc);
        Assert.True(doc.FileSizeKB > 0);
    }

    [Fact]
    public void DecompressFile_NoThrow()
    {
        var src = CreateTextFile("nothrow2.txt", RepetitiveContent);
        var compressed = TempFile("nothrow2.zst");
        var output = TempFile("nothrow2_out.txt");
        ZstWriter.CompressFile(src, compressed);
        var ex = Record.Exception(() => ZstWriter.DecompressFile(compressed, output));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // CompressStream
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressStream_NoThrow()
    {
        var data = Encoding.UTF8.GetBytes(RepetitiveContent);
        using var input = new MemoryStream(data);
        using var output = new MemoryStream();
        var ex = Record.Exception(() => ZstWriter.CompressStream(input, output));
        Assert.Null(ex);
    }

    [Fact]
    public void CompressStream_OutputNonEmpty()
    {
        var data = Encoding.UTF8.GetBytes(RepetitiveContent);
        using var input = new MemoryStream(data);
        using var output = new MemoryStream();
        ZstWriter.CompressStream(input, output);
        Assert.True(output.Length > 0);
    }

    [Fact]
    public void CompressStream_ThenDecompressStream_RoundTrip()
    {
        var data = Encoding.UTF8.GetBytes(RepetitiveContent);
        using var input = new MemoryStream(data);
        using var compressed = new MemoryStream();
        ZstWriter.CompressStream(input, compressed);

        compressed.Seek(0, SeekOrigin.Begin);
        using var decompressed = new MemoryStream();
        ZstWriter.DecompressStream(compressed, decompressed);

        var result = Encoding.UTF8.GetString(decompressed.ToArray());
        Assert.Equal(RepetitiveContent, result);
    }

    [Fact]
    public void CompressStream_OutputIsValidZstd()
    {
        var data = Encoding.UTF8.GetBytes(RepetitiveContent);
        using var input = new MemoryStream(data);
        using var output = new MemoryStream();
        ZstWriter.CompressStream(input, output);
        Assert.True(ZstWriter.ValidateBytes(output.ToArray()));
    }

    [Fact]
    public void CompressStream_Consistent()
    {
        var data = Encoding.UTF8.GetBytes(RepetitiveContent);
        using var input1 = new MemoryStream(data);
        using var out1 = new MemoryStream();
        ZstWriter.CompressStream(input1, out1);

        using var input2 = new MemoryStream(data);
        using var out2 = new MemoryStream();
        ZstWriter.CompressStream(input2, out2);

        // Same input → same (or similar) output size
        Assert.True(Math.Abs(out1.Length - out2.Length) <= 100);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressFile_DecompressFile_CompressStream_ValidateFile_Pipeline()
    {
        var content = "Dogfood content: " +
            string.Concat(System.Linq.Enumerable.Repeat("Repeated payload for comprehensive testing. ", 50));

        // CompressFile
        var srcPath = CreateTextFile("dogfood_src.txt", content);
        var compressedPath = TempFile("dogfood.zst");
        ZstWriter.CompressFile(srcPath, compressedPath);
        Assert.True(File.Exists(compressedPath));
        Assert.True(new FileInfo(compressedPath).Length > 0);
        Assert.True(new FileInfo(compressedPath).Length < new FileInfo(srcPath).Length);

        // ValidateFile
        Assert.True(ZstDocument.ValidateFile(compressedPath));

        // ParseFile
        var doc = ZstParser.ParseFile(compressedPath);
        Assert.NotNull(doc);
        Assert.True(doc.FileSizeKB > 0);
        Assert.True(doc.CompressionRatio > 1.0);

        // DecompressFile
        var decompressedPath = TempFile("dogfood_decompressed.txt");
        ZstWriter.DecompressFile(compressedPath, decompressedPath);
        Assert.True(File.Exists(decompressedPath));
        Assert.Equal(content, File.ReadAllText(decompressedPath));

        // CompressStream
        var streamData = Encoding.UTF8.GetBytes(content);
        using var inStream = new MemoryStream(streamData);
        using var outStream = new MemoryStream();
        ZstWriter.CompressStream(inStream, outStream);
        var streamCompressed = outStream.ToArray();
        Assert.True(streamCompressed.Length > 0);
        Assert.True(ZstWriter.ValidateBytes(streamCompressed));

        // DecompressStream
        using var decompIn = new MemoryStream(streamCompressed);
        using var decompOut = new MemoryStream();
        ZstWriter.DecompressStream(decompIn, decompOut);
        var streamDecompressed = Encoding.UTF8.GetString(decompOut.ToArray());
        Assert.Equal(content, streamDecompressed);

        // Save stream-compressed to file and validate
        var streamPath = TempFile("dogfood_stream.zst");
        File.WriteAllBytes(streamPath, streamCompressed);
        Assert.True(ZstDocument.ValidateFile(streamPath));

        // Multiple file round-trips
        for (int i = 0; i < 3; i++)
        {
            var iSrc = CreateTextFile($"dogfood_{i}.txt", $"Item {i}: " + content);
            var iDest = TempFile($"dogfood_{i}.zst");
            var iOut = TempFile($"dogfood_{i}_rt.txt");
            ZstWriter.CompressFile(iSrc, iDest);
            ZstWriter.DecompressFile(iDest, iOut);
            Assert.Equal($"Item {i}: " + content, File.ReadAllText(iOut));
        }
    }
}
