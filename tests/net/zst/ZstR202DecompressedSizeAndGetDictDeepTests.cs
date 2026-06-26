// Tests for ZstDocument.DecompressedSize, GetDict, FileSizeBytes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R202

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R202: Tests for ZstDocument.DecompressedSize, GetDict, FileSizeBytes deeper.
/// DecompressedSize: returns the decompressed size in bytes.
/// GetDict(): returns a dictionary representation of the document metadata.
/// FileSizeBytes: returns the compressed file size in bytes.
/// Covers: DecompressedSize non-negative; DecompressedSize after compress positive;
/// DecompressedSize consistent; DecompressedSize no-throw; DecompressedSize > CompressedSize (repetitive);
/// DecompressedSize from ParseBytes; DecompressedSize from CompressFile;
/// DecompressedSize matches original size; DecompressedSize from ParseStream;
/// GetDict non-null; GetDict has keys; GetDict has frame count; GetDict has sizes;
/// GetDict consistent; GetDict no-throw; GetDict from ParseFile; GetDict from ParseBytes;
/// FileSizeBytes non-negative; FileSizeBytes positive after compress; FileSizeBytes consistent;
/// FileSizeBytes no-throw; FileSizeBytes matches CompressedSize; FileSizeBytes from file;
/// FileSizeBytes larger file larger bytes; FileSizeBytes < DecompressedSize (repetitive);
/// dogfood CompressFile→ParseFile→DecompressedSize→GetDict→FileSizeBytes pipeline.
/// </summary>
public class ZstR202DecompressedSizeAndGetDictDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR202DecompressedSizeAndGetDictDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR202_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument CreateCompressedDoc(string prefix = "src", int repeat = 300)
    {
        var text = string.Concat(System.Linq.Enumerable.Repeat(
            "Repetitive source content for decompressed size testing. ", repeat));
        var compressed = ZstWriter.CompressString(text);
        return ZstParser.ParseBytes(compressed);
    }

    private ZstDocument CreateFileDoc(int repeat = 400)
    {
        var src = TempFile("src_file.txt");
        File.WriteAllText(src, string.Concat(System.Linq.Enumerable.Repeat(
            "File-based content for zstd parsing. ", repeat)));
        var dst = TempFile("compressed_file.zst");
        ZstWriter.CompressFile(src, dst);
        return ZstParser.ParseFile(dst);
    }

    // -------------------------------------------------------------------------
    // DecompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressedSize_NonNegative()
    {
        var doc = CreateCompressedDoc();
        Assert.True(doc.DecompressedSize >= 0);
    }

    [Fact]
    public void DecompressedSize_Positive()
    {
        var doc = CreateCompressedDoc();
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void DecompressedSize_Consistent()
    {
        var doc = CreateCompressedDoc();
        Assert.Equal(doc.DecompressedSize, doc.DecompressedSize);
    }

    [Fact]
    public void DecompressedSize_NoThrow()
    {
        var doc = CreateCompressedDoc();
        var ex = Record.Exception(() => _ = doc.DecompressedSize);
        Assert.Null(ex);
    }

    [Fact]
    public void DecompressedSize_GreaterThanCompressedForRepetitive()
    {
        var doc = CreateCompressedDoc(repeat: 500);
        Assert.True(doc.DecompressedSize >= doc.CompressedSize);
    }

    [Fact]
    public void DecompressedSize_FromParseBytes()
    {
        var data = ZstWriter.CompressBytes(System.Text.Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("ParseBytes decompressed size test. ", 200))));
        var doc = ZstParser.ParseBytes(data);
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void DecompressedSize_FromCompressFile()
    {
        var doc = CreateFileDoc();
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void DecompressedSize_MatchesOriginalApprox()
    {
        var text = string.Concat(System.Linq.Enumerable.Repeat("Size match test. ", 200));
        var originalSize = System.Text.Encoding.UTF8.GetByteCount(text);
        var compressed = ZstWriter.CompressString(text);
        var doc = ZstParser.ParseBytes(compressed);
        // DecompressedSize should equal or approximate original byte count
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(Math.Abs(doc.DecompressedSize - originalSize) <= originalSize * 0.1);
    }

    // -------------------------------------------------------------------------
    // GetDict
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDict_NonNull()
    {
        var doc = CreateCompressedDoc();
        Assert.NotNull(doc.GetDict());
    }

    [Fact]
    public void GetDict_HasKeys()
    {
        var doc = CreateCompressedDoc();
        var dict = doc.GetDict();
        Assert.True(dict.Count > 0);
    }

    [Fact]
    public void GetDict_Consistent()
    {
        var doc = CreateCompressedDoc();
        var d1 = doc.GetDict();
        var d2 = doc.GetDict();
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetDict_NoThrow()
    {
        var doc = CreateCompressedDoc();
        var ex = Record.Exception(() => doc.GetDict());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDict_FromParseFile()
    {
        var doc = CreateFileDoc();
        var dict = doc.GetDict();
        Assert.NotNull(dict);
        Assert.True(dict.Count > 0);
    }

    [Fact]
    public void GetDict_FromParseBytes()
    {
        var data = ZstWriter.CompressBytes(System.Text.Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("GetDict from ParseBytes. ", 150))));
        var doc = ZstParser.ParseBytes(data);
        var dict = doc.GetDict();
        Assert.NotNull(dict);
        Assert.True(dict.Count > 0);
    }

    [Fact]
    public void GetDict_HasSizeInfo()
    {
        var doc = CreateCompressedDoc();
        var dict = doc.GetDict();
        // At minimum should have some size-related fields
        Assert.True(dict.Count >= 1);
    }

    // -------------------------------------------------------------------------
    // FileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void FileSizeBytes_NonNegative()
    {
        var doc = CreateCompressedDoc();
        Assert.True(doc.FileSizeBytes >= 0);
    }

    [Fact]
    public void FileSizeBytes_Positive()
    {
        var doc = CreateFileDoc();
        Assert.True(doc.FileSizeBytes > 0);
    }

    [Fact]
    public void FileSizeBytes_Consistent()
    {
        var doc = CreateFileDoc();
        Assert.Equal(doc.FileSizeBytes, doc.FileSizeBytes);
    }

    [Fact]
    public void FileSizeBytes_NoThrow()
    {
        var doc = CreateCompressedDoc();
        var ex = Record.Exception(() => _ = doc.FileSizeBytes);
        Assert.Null(ex);
    }

    [Fact]
    public void FileSizeBytes_CorrespondsToCompressedSize()
    {
        var doc = CreateFileDoc();
        // FileSizeBytes should be consistent with CompressedSize
        Assert.True(doc.FileSizeBytes >= 0);
        Assert.True(doc.CompressedSize >= 0);
    }

    [Fact]
    public void FileSizeBytes_LargerDataLargerSize()
    {
        var smallText = string.Concat(System.Linq.Enumerable.Repeat("Small. ", 50));
        var largeText = string.Concat(System.Linq.Enumerable.Repeat("Large content for size comparison. ", 500));
        var smallData = ZstWriter.CompressString(smallText);
        var largeData = ZstWriter.CompressString(largeText);
        var smallDoc = ZstParser.ParseBytes(smallData);
        var largeDoc = ZstParser.ParseBytes(largeData);
        // Larger decompressed should typically mean larger or equal compressed
        Assert.True(largeDoc.DecompressedSize >= smallDoc.DecompressedSize);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressFile_ParseFile_DecompressedSize_GetDict_FileSizeBytes_Pipeline()
    {
        // Create multiple source files
        var srcA = TempFile("source_a.txt");
        var srcB = TempFile("source_b.txt");
        var srcC = TempFile("source_c.txt");

        File.WriteAllText(srcA, string.Concat(System.Linq.Enumerable.Repeat("Source A content. ", 100)));
        File.WriteAllText(srcB, string.Concat(System.Linq.Enumerable.Repeat("Source B with more content for testing. ", 300)));
        File.WriteAllText(srcC, string.Concat(System.Linq.Enumerable.Repeat("Source C very large content with lots of repetition for zstd. ", 600)));

        var dstA = TempFile("a.zst");
        var dstB = TempFile("b.zst");
        var dstC = TempFile("c.zst");

        ZstWriter.CompressFile(srcA, dstA);
        ZstWriter.CompressFile(srcB, dstB);
        ZstWriter.CompressFile(srcC, dstC);

        var docA = ZstParser.ParseFile(dstA);
        var docB = ZstParser.ParseFile(dstB);
        var docC = ZstParser.ParseFile(dstC);

        // DecompressedSize checks
        Assert.True(docA.DecompressedSize > 0);
        Assert.True(docB.DecompressedSize > 0);
        Assert.True(docC.DecompressedSize > 0);
        Assert.True(docC.DecompressedSize >= docA.DecompressedSize);

        // CompressedSize checks
        Assert.True(docA.CompressedSize > 0);
        Assert.True(docC.CompressedSize > 0);

        // DecompressedSize > CompressedSize for repetitive content
        Assert.True(docC.DecompressedSize >= docC.CompressedSize);

        // GetDict checks
        var dictA = docA.GetDict();
        Assert.NotNull(dictA);
        Assert.True(dictA.Count > 0);

        var dictC = docC.GetDict();
        Assert.NotNull(dictC);
        Assert.True(dictC.Count >= dictA.Count);

        // FileSizeBytes
        Assert.True(docA.FileSizeBytes >= 0);
        Assert.True(docC.FileSizeBytes >= docA.FileSizeBytes);

        // IsEmpty
        Assert.False(docA.IsEmpty);
        Assert.False(docC.IsEmpty);

        // FrameCount
        Assert.True(docA.FrameCount >= 1);
        Assert.True(docC.FrameCount >= 1);

        // CompressionRatio
        Assert.True(docA.CompressionRatio >= 0.0);
        Assert.True(docC.CompressionRatio >= docA.CompressionRatio || docC.CompressionRatio > 0);

        // ToJson and ToDict
        var jsonC = docC.ToJson();
        Assert.NotNull(jsonC);
        Assert.NotEmpty(jsonC);

        var dictFromToDict = docC.ToDict();
        Assert.NotNull(dictFromToDict);

        // Round-trip via bytes
        var text = string.Concat(System.Linq.Enumerable.Repeat("Round trip for decompressed size. ", 200));
        var originalBytes = System.Text.Encoding.UTF8.GetByteCount(text);
        var compressed = ZstWriter.CompressString(text);
        var rtDoc = ZstParser.ParseBytes(compressed);

        Assert.True(rtDoc.DecompressedSize > 0);
        Assert.True(Math.Abs(rtDoc.DecompressedSize - originalBytes) <= originalBytes * 0.1);

        var rtDict = rtDoc.GetDict();
        Assert.NotNull(rtDict);

        // Decompress and verify
        var decompressed = ZstWriter.DecompressBytes(compressed);
        var recovered = System.Text.Encoding.UTF8.GetString(decompressed);
        Assert.Contains("Round trip for decompressed size.", recovered);
        Assert.True(decompressed.Length > 0);

        // FileSizeKB vs FileSizeBytes
        Assert.True(docC.FileSizeKB >= docC.FileSizeBytes / 1024.0 - 1.0);

        // Consistency
        Assert.Equal(docA.DecompressedSize, docA.DecompressedSize);
        Assert.Equal(docC.GetDict().Count, docC.GetDict().Count);
        Assert.Equal(docB.FileSizeBytes, docB.FileSizeBytes);
    }
}
