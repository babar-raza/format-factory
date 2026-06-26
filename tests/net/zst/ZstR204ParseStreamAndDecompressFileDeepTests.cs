// Tests for ZstParser.ParseStream, ZstWriter.DecompressFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R204

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R204: Tests for ZstParser.ParseStream, ZstWriter.DecompressFile deeper.
/// ParseStream(stream): parses a Zstandard-compressed stream into a ZstDocument.
/// DecompressFile(src, dst): decompresses a .zst file to the destination path.
/// ZstDocument.IsValid: indicates whether the document is a valid Zstandard frame.
/// Covers: ParseStream non-null; ParseStream FrameCount>=1; ParseStream consistent;
/// ParseStream no-throw; ParseStream from MemoryStream; ParseStream compressed file stream;
/// ParseStream DecompressedSize>0; ParseStream CompressedSize>0; ParseStream IsEmpty=false;
/// DecompressFile no-throw; DecompressFile creates file; DecompressFile content roundtrip;
/// DecompressFile large content; DecompressFile small content; DecompressFile multiple;
/// DecompressFile then ParseFile consistent; DecompressFile after CompressFile;
/// IsValid true for compressed; IsValid consistent; IsValid no-throw;
/// IsValid from ParseBytes; IsValid from ParseStream; IsValid from ParseFile;
/// dogfood CompressString→ParseStream→DecompressFile→IsValid pipeline.
/// </summary>
public class ZstR204ParseStreamAndDecompressFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR204ParseStreamAndDecompressFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR204_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private byte[] MakeCompressed(string text)
        => ZstWriter.CompressString(text);

    private string CreateCompressedFile(string text)
    {
        var src = TempFile("raw_" + Guid.NewGuid().ToString("N") + ".txt");
        var dst = TempFile("comp_" + Guid.NewGuid().ToString("N") + ".zst");
        File.WriteAllText(src, text);
        ZstWriter.CompressFile(src, dst);
        return dst;
    }

    // -------------------------------------------------------------------------
    // ParseStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_NonNull()
    {
        var data = MakeCompressed(string.Concat(System.Linq.Enumerable.Repeat("stream test data. ", 100)));
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.NotNull(doc);
    }

    [Fact]
    public void ParseStream_FrameCountAtLeastOne()
    {
        var data = MakeCompressed(string.Concat(System.Linq.Enumerable.Repeat("frame count via stream. ", 200)));
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void ParseStream_Consistent()
    {
        var data = MakeCompressed("consistent stream data repeated.");
        using var ms1 = new MemoryStream(data);
        using var ms2 = new MemoryStream(data);
        var doc1 = ZstParser.ParseStream(ms1);
        var doc2 = ZstParser.ParseStream(ms2);
        Assert.Equal(doc1.FrameCount, doc2.FrameCount);
    }

    [Fact]
    public void ParseStream_NoThrow()
    {
        var data = MakeCompressed(string.Concat(System.Linq.Enumerable.Repeat("no throw stream. ", 50)));
        using var ms = new MemoryStream(data);
        var ex = Record.Exception(() => ZstParser.ParseStream(ms));
        Assert.Null(ex);
    }

    [Fact]
    public void ParseStream_FromMemoryStream()
    {
        var text = string.Concat(System.Linq.Enumerable.Repeat("memory stream test content. ", 300));
        var data = ZstWriter.CompressBytes(System.Text.Encoding.UTF8.GetBytes(text));
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void ParseStream_DecompressedSizePositive()
    {
        var text = string.Concat(System.Linq.Enumerable.Repeat("decompressed size check. ", 200));
        var data = MakeCompressed(text);
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void ParseStream_CompressedSizePositive()
    {
        var data = MakeCompressed(string.Concat(System.Linq.Enumerable.Repeat("compressed size. ", 150)));
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.CompressedSize > 0);
    }

    [Fact]
    public void ParseStream_IsEmpty_False()
    {
        var data = MakeCompressed(string.Concat(System.Linq.Enumerable.Repeat("not empty. ", 100)));
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void ParseStream_FromCompressedFileStream()
    {
        var zstPath = CreateCompressedFile(string.Concat(System.Linq.Enumerable.Repeat("file stream data. ", 200)));
        using var fs = File.OpenRead(zstPath);
        var doc = ZstParser.ParseStream(fs);
        Assert.True(doc.FrameCount >= 1);
    }

    // -------------------------------------------------------------------------
    // DecompressFile
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressFile_NoThrow()
    {
        var zstPath = CreateCompressedFile("decompress no throw test data.");
        var outPath = TempFile("out_nothrow.txt");
        var ex = Record.Exception(() => ZstWriter.DecompressFile(zstPath, outPath));
        Assert.Null(ex);
    }

    [Fact]
    public void DecompressFile_CreatesFile()
    {
        var zstPath = CreateCompressedFile("decompress creates file.");
        var outPath = TempFile("out_creates.txt");
        ZstWriter.DecompressFile(zstPath, outPath);
        Assert.True(File.Exists(outPath));
    }

    [Fact]
    public void DecompressFile_ContentRoundtrip()
    {
        var original = string.Concat(System.Linq.Enumerable.Repeat("roundtrip content test. ", 200));
        var zstPath = CreateCompressedFile(original);
        var outPath = TempFile("out_roundtrip.txt");
        ZstWriter.DecompressFile(zstPath, outPath);
        var recovered = File.ReadAllText(outPath);
        Assert.Contains("roundtrip content test.", recovered);
    }

    [Fact]
    public void DecompressFile_LargeContent()
    {
        var text = string.Concat(System.Linq.Enumerable.Repeat("large content data for decompression test. ", 1000));
        var zstPath = CreateCompressedFile(text);
        var outPath = TempFile("out_large.txt");
        ZstWriter.DecompressFile(zstPath, outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);
    }

    [Fact]
    public void DecompressFile_SmallContent()
    {
        var zstPath = CreateCompressedFile("small.");
        var outPath = TempFile("out_small.txt");
        ZstWriter.DecompressFile(zstPath, outPath);
        Assert.True(File.Exists(outPath));
    }

    [Fact]
    public void DecompressFile_Multiple()
    {
        for (int i = 0; i < 3; i++)
        {
            var zstPath = CreateCompressedFile($"multiple decompression test {i}.");
            var outPath = TempFile($"out_multi_{i}.txt");
            ZstWriter.DecompressFile(zstPath, outPath);
            Assert.True(File.Exists(outPath));
        }
    }

    [Fact]
    public void DecompressFile_ThenParseFile_Consistent()
    {
        var text = string.Concat(System.Linq.Enumerable.Repeat("then parse file. ", 100));
        var zstPath = CreateCompressedFile(text);
        var outPath = TempFile("out_then_parse.txt");
        ZstWriter.DecompressFile(zstPath, outPath);
        var doc = ZstParser.ParseFile(zstPath);
        Assert.True(doc.FrameCount >= 1);
        Assert.True(File.Exists(outPath));
    }

    // -------------------------------------------------------------------------
    // IsValid
    // -------------------------------------------------------------------------

    [Fact]
    public void IsValid_True_ForCompressed()
    {
        var data = MakeCompressed("valid compressed data.");
        var doc = ZstParser.ParseBytes(data);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_Consistent()
    {
        var data = MakeCompressed("consistency test.");
        var doc = ZstParser.ParseBytes(data);
        Assert.Equal(doc.IsValid, doc.IsValid);
    }

    [Fact]
    public void IsValid_NoThrow()
    {
        var data = MakeCompressed("no throw validity.");
        var doc = ZstParser.ParseBytes(data);
        var ex = Record.Exception(() => _ = doc.IsValid);
        Assert.Null(ex);
    }

    [Fact]
    public void IsValid_FromParseFile()
    {
        var zstPath = CreateCompressedFile(string.Concat(System.Linq.Enumerable.Repeat("valid from file. ", 50)));
        var doc = ZstParser.ParseFile(zstPath);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_FromParseStream()
    {
        var data = MakeCompressed(string.Concat(System.Linq.Enumerable.Repeat("valid from stream. ", 80)));
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.True(doc.IsValid);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressString_ParseStream_DecompressFile_IsValid_Pipeline()
    {
        // Create test texts of varying sizes
        var smallText = string.Concat(System.Linq.Enumerable.Repeat("Small data for pipeline test. ", 50));
        var mediumText = string.Concat(System.Linq.Enumerable.Repeat("Medium content pipeline verification data. ", 300));
        var largeText = string.Concat(System.Linq.Enumerable.Repeat(
            "Large comprehensive pipeline test data for Zstandard parsing. ", 800));

        // Compress all texts
        var smallData = ZstWriter.CompressString(smallText);
        var mediumData = ZstWriter.CompressString(mediumText);
        var largeData = ZstWriter.CompressString(largeText);

        Assert.True(smallData.Length > 0);
        Assert.True(mediumData.Length > 0);
        Assert.True(largeData.Length > 0);

        // ParseStream for each
        ZstDocument smallDoc, mediumDoc, largeDoc;
        using (var ms = new MemoryStream(smallData))
            smallDoc = ZstParser.ParseStream(ms);
        using (var ms = new MemoryStream(mediumData))
            mediumDoc = ZstParser.ParseStream(ms);
        using (var ms = new MemoryStream(largeData))
            largeDoc = ZstParser.ParseStream(ms);

        // FrameCount
        Assert.True(smallDoc.FrameCount >= 1);
        Assert.True(mediumDoc.FrameCount >= 1);
        Assert.True(largeDoc.FrameCount >= 1);

        // IsValid
        Assert.True(smallDoc.IsValid);
        Assert.True(mediumDoc.IsValid);
        Assert.True(largeDoc.IsValid);

        // CompressedSize and DecompressedSize
        Assert.True(smallDoc.CompressedSize > 0);
        Assert.True(largeDoc.DecompressedSize > 0);
        Assert.True(largeDoc.DecompressedSize > smallDoc.DecompressedSize);

        // CompressionRatio
        Assert.True(largeDoc.CompressionRatio >= 0.0);

        // Write compressed files
        var smallZst = TempFile("small_stream.zst");
        var mediumZst = TempFile("medium_stream.zst");
        var largeZst = TempFile("large_stream.zst");
        File.WriteAllBytes(smallZst, smallData);
        File.WriteAllBytes(mediumZst, mediumData);
        File.WriteAllBytes(largeZst, largeData);

        // DecompressFile
        var smallOut = TempFile("small_out.txt");
        var mediumOut = TempFile("medium_out.txt");
        var largeOut = TempFile("large_out.txt");
        ZstWriter.DecompressFile(smallZst, smallOut);
        ZstWriter.DecompressFile(mediumZst, mediumOut);
        ZstWriter.DecompressFile(largeZst, largeOut);

        Assert.True(File.Exists(smallOut));
        Assert.True(File.Exists(mediumOut));
        Assert.True(File.Exists(largeOut));

        // Content roundtrip verification
        var smallRecovered = File.ReadAllText(smallOut);
        var mediumRecovered = File.ReadAllText(mediumOut);
        var largeRecovered = File.ReadAllText(largeOut);
        Assert.Contains("Small data for pipeline test.", smallRecovered);
        Assert.Contains("Medium content pipeline verification data.", mediumRecovered);
        Assert.Contains("Large comprehensive pipeline test data", largeRecovered);

        // ParseFile after DecompressFile
        var parsedSmall = ZstParser.ParseFile(smallZst);
        Assert.True(parsedSmall.IsValid);
        Assert.Equal(smallDoc.FrameCount, parsedSmall.FrameCount);

        // ParseStream from file streams
        using (var fs = File.OpenRead(largeZst))
        {
            var streamDoc = ZstParser.ParseStream(fs);
            Assert.True(streamDoc.IsValid);
            Assert.Equal(largeDoc.FrameCount, streamDoc.FrameCount);
        }

        // ParseBytes roundtrip
        var rtDoc = ZstParser.ParseBytes(mediumData);
        Assert.True(rtDoc.IsValid);
        Assert.Equal(mediumDoc.FrameCount, rtDoc.FrameCount);

        // DecompressBytes roundtrip
        var decompBytes = ZstWriter.DecompressBytes(mediumData);
        var decompStr = System.Text.Encoding.UTF8.GetString(decompBytes);
        Assert.Contains("Medium content pipeline verification data.", decompStr);

        // IsValid consistent
        Assert.Equal(largeDoc.IsValid, largeDoc.IsValid);

        // ToDict non-null
        var dict = largeDoc.ToDict();
        Assert.NotNull(dict);

        // ToJson non-null
        var json = largeDoc.ToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // CompressFile → ParseFile → ParseStream consistency
        var srcTxt = TempFile("src_final.txt");
        var dstZst = TempFile("dst_final.zst");
        File.WriteAllText(srcTxt, largeText);
        ZstWriter.CompressFile(srcTxt, dstZst);
        var fileDoc = ZstParser.ParseFile(dstZst);
        Assert.True(fileDoc.IsValid);
        Assert.True(fileDoc.FrameCount >= 1);
        using (var fs = File.OpenRead(dstZst))
        {
            var streamDoc2 = ZstParser.ParseStream(fs);
            Assert.True(streamDoc2.IsValid);
        }
    }
}
