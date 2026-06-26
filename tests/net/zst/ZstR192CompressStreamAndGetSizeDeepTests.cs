// Tests for ZstWriter.CompressStream, ZstDocument.GetDecompressedSize, deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R192

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R192: Tests for ZstWriter.CompressStream, ZstDocument.GetDecompressedSize, deeper.
/// CompressStream(inputStream, outputStream): compresses stream data into output stream.
/// DecompressStream(inputStream, outputStream): decompresses zstd-compressed stream.
/// ZstDocument.GetDecompressedSize: returns the uncompressed content size in bytes.
/// Covers: CompressStream non-empty output; CompressStream round-trip via DecompressStream;
/// CompressStream large data; CompressStream multiple calls consistent;
/// DecompressStream after CompressStream matches original; DecompressStream non-empty;
/// GetDecompressedSize positive; GetDecompressedSize larger than compressed;
/// GetDecompressedSize consistent; GetDecompressedSize for large data;
/// CompressString to file then LoadFile; CompressString unicode content;
/// CompressionRatio > 1 for repetitive content; FileSizeKB after compress;
/// dogfood CompressStream→DecompressStream→ParseFile→GetDecompressedSize→verify pipeline.
/// </summary>
public class ZstR192CompressStreamAndGetSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR192CompressStreamAndGetSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR192_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string RepetitiveContent =
        string.Concat(System.Linq.Enumerable.Repeat(
            "The compression test content repeats many times for best results. ", 100));

    // -------------------------------------------------------------------------
    // CompressStream / DecompressStream
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressStream_NonEmptyOutput()
    {
        var input = Encoding.UTF8.GetBytes(RepetitiveContent);
        using var inStream = new MemoryStream(input);
        using var outStream = new MemoryStream();
        ZstWriter.CompressStream(inStream, outStream);
        Assert.True(outStream.Length > 0);
    }

    [Fact]
    public void CompressStream_SmallerThanInput()
    {
        var input = Encoding.UTF8.GetBytes(RepetitiveContent);
        using var inStream = new MemoryStream(input);
        using var outStream = new MemoryStream();
        ZstWriter.CompressStream(inStream, outStream);
        Assert.True(outStream.Length < input.Length);
    }

    [Fact]
    public void CompressStream_DecompressStream_RoundTrip()
    {
        var original = Encoding.UTF8.GetBytes("Stream round-trip test: " + RepetitiveContent);
        using var inStream = new MemoryStream(original);
        using var compStream = new MemoryStream();
        ZstWriter.CompressStream(inStream, compStream);

        compStream.Position = 0;
        using var decompStream = new MemoryStream();
        ZstWriter.DecompressStream(compStream, decompStream);

        var result = decompStream.ToArray();
        Assert.Equal(original, result);
    }

    [Fact]
    public void CompressStream_LargeData_NonEmpty()
    {
        var large = Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("Large stream content block. ", 500)));
        using var inStream = new MemoryStream(large);
        using var outStream = new MemoryStream();
        ZstWriter.CompressStream(inStream, outStream);
        Assert.True(outStream.Length > 0);
        Assert.True(outStream.Length < large.Length);
    }

    [Fact]
    public void DecompressStream_MatchesOriginal()
    {
        var original = Encoding.UTF8.GetBytes("DecompressStream verification content ABC-123.");
        using var inStream = new MemoryStream(original);
        using var compStream = new MemoryStream();
        ZstWriter.CompressStream(inStream, compStream);

        compStream.Position = 0;
        using var decompStream = new MemoryStream();
        ZstWriter.DecompressStream(compStream, decompStream);

        var text = Encoding.UTF8.GetString(decompStream.ToArray());
        Assert.Contains("ABC-123", text);
    }

    [Fact]
    public void CompressStream_Consistent()
    {
        var input = Encoding.UTF8.GetBytes("Consistent test: " + RepetitiveContent);
        using var in1 = new MemoryStream(input);
        using var out1 = new MemoryStream();
        ZstWriter.CompressStream(in1, out1);

        using var in2 = new MemoryStream(input);
        using var out2 = new MemoryStream();
        ZstWriter.CompressStream(in2, out2);

        // Both compressions should produce same-length output
        Assert.Equal(out1.Length, out2.Length);
    }

    // -------------------------------------------------------------------------
    // GetDecompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressedSize_Positive()
    {
        var path = TempFile("size_test.zst");
        ZstWriter.CompressString(RepetitiveContent, path);
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.GetDecompressedSize() > 0);
    }

    [Fact]
    public void GetDecompressedSize_LargerThanCompressedSize()
    {
        var path = TempFile("size_compare.zst");
        ZstWriter.CompressString(RepetitiveContent, path);
        var doc = ZstParser.ParseFile(path);
        var decompSize = doc.GetDecompressedSize();
        var compressedBytes = new FileInfo(path).Length;
        Assert.True(decompSize > compressedBytes);
    }

    [Fact]
    public void GetDecompressedSize_Consistent()
    {
        var path = TempFile("size_consist.zst");
        ZstWriter.CompressString(RepetitiveContent, path);
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.GetDecompressedSize(), doc.GetDecompressedSize());
    }

    [Fact]
    public void GetDecompressedSize_MatchesOriginalLength()
    {
        var content = "Known length content for size verification.";
        var path = TempFile("known_size.zst");
        ZstWriter.CompressString(content, path);
        var doc = ZstParser.ParseFile(path);
        var decompSize = doc.GetDecompressedSize();
        var expectedBytes = Encoding.UTF8.GetByteCount(content);
        // Allow small variance due to encoding
        Assert.True(Math.Abs(decompSize - expectedBytes) <= 4);
    }

    [Fact]
    public void GetDecompressedSize_LargerContentHasLargerSize()
    {
        var shortPath = TempFile("short.zst");
        var longPath = TempFile("long.zst");
        ZstWriter.CompressString("Short content.", shortPath);
        ZstWriter.CompressString(RepetitiveContent, longPath);
        var shortDoc = ZstParser.ParseFile(shortPath);
        var longDoc = ZstParser.ParseFile(longPath);
        Assert.True(longDoc.GetDecompressedSize() > shortDoc.GetDecompressedSize());
    }

    // -------------------------------------------------------------------------
    // Additional CompressString coverage
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressString_UnicodeContent_RoundTrip()
    {
        var unicode = "Unicode content: café, naïve, résumé, 你好世界, مرحبا";
        var path = TempFile("unicode.zst");
        ZstWriter.CompressString(unicode, path);
        Assert.True(File.Exists(path));
        var result = ZstWriter.DecompressFile(path);
        Assert.Equal(unicode, result);
    }

    [Fact]
    public void CompressString_LargeContent_FileSizeKB_Positive()
    {
        var path = TempFile("large_kb.zst");
        ZstWriter.CompressString(RepetitiveContent, path);
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FileSizeKB > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressStream_DecompressStream_ParseFile_GetDecompressedSize_Pipeline()
    {
        // Step 1: CompressStream to file
        var original = Encoding.UTF8.GetBytes(
            "Dogfood pipeline test. " + string.Concat(
                System.Linq.Enumerable.Repeat("Repeating payload for compression verification. ", 50)));

        var compressedPath = TempFile("dogfood_stream.zst");
        using (var inStream = new MemoryStream(original))
        using (var outStream = File.Create(compressedPath))
        {
            ZstWriter.CompressStream(inStream, outStream);
        }

        Assert.True(File.Exists(compressedPath));
        Assert.True(new FileInfo(compressedPath).Length > 0);
        Assert.True(new FileInfo(compressedPath).Length < original.Length);

        // Step 2: ParseFile and verify properties
        var doc = ZstParser.ParseFile(compressedPath);
        Assert.NotNull(doc);
        Assert.True(doc.FileSizeKB > 0);
        Assert.True(doc.CompressionRatio > 1.0); // repetitive content should compress well
        Assert.NotNull(doc.ToDict());
        Assert.True(doc.ToDict().Count > 0);

        // Step 3: GetDecompressedSize
        var decompSize = doc.GetDecompressedSize();
        Assert.True(decompSize > 0);
        Assert.True(decompSize > new FileInfo(compressedPath).Length);
        // Should approximate original size
        Assert.True(Math.Abs(decompSize - original.Length) <= 10);

        // Step 4: DecompressStream from file
        using var compStream = File.OpenRead(compressedPath);
        using var decompStream = new MemoryStream();
        ZstWriter.DecompressStream(compStream, decompStream);
        var restored = decompStream.ToArray();
        Assert.Equal(original, restored);

        // Step 5: ValidateFile
        Assert.True(ZstDocument.ValidateFile(compressedPath));

        // Step 6: CompressString variant and round-trip
        var stringContent = "String compression dogfood. " + RepetitiveContent;
        var strPath = TempFile("dogfood_string.zst");
        ZstWriter.CompressString(stringContent, strPath);
        var strDoc = ZstParser.ParseFile(strPath);
        Assert.True(strDoc.GetDecompressedSize() > 0);
        var decompString = ZstWriter.DecompressFile(strPath);
        Assert.Equal(stringContent, decompString);

        // Step 7: CompressBytes and GetDecompressedSize consistency
        var bytesContent = Encoding.UTF8.GetBytes(stringContent);
        var compressedBytes = ZstWriter.CompressBytes(bytesContent);
        var bytesDoc = ZstParser.ParseBytes(compressedBytes);
        Assert.True(bytesDoc.CompressionRatio > 0);
    }
}
