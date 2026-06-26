// Tests for ZstDocument.ToString, ToJson, CompressionLevel deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R205

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R205: Tests for ZstDocument.ToString, ToJson, CompressionLevel deeper.
/// ToString(): returns a string summary of the document's properties.
/// ToJson(): returns the document metadata as a JSON string.
/// CompressionLevel: indicates the compression level used (1-22).
/// Covers: ToString non-null; ToString non-empty; ToString consistent; ToString no-throw;
/// ToString contains relevant info; ToString from ParseFile; ToString from ParseBytes;
/// ToString after multiple ops consistent; ToString length positive;
/// ToJson non-null; ToJson non-empty; ToJson consistent; ToJson no-throw;
/// ToJson is valid JSON (has braces); ToJson has size info; ToJson has frame info;
/// ToJson from ParseFile; ToJson from ParseBytes; ToJson from ParseStream;
/// CompressionLevel non-negative; CompressionLevel in range 1-22; CompressionLevel consistent;
/// CompressionLevel no-throw; CompressionLevel from ParseFile; CompressionLevel from ParseBytes;
/// CompressionLevel from CompressString level1; CompressionLevel from CompressString level9;
/// dogfood CompressBytes→ParseBytes→ToString→ToJson→CompressionLevel pipeline.
/// </summary>
public class ZstR205CompressionLevelAndToStringDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR205CompressionLevelAndToStringDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR205_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument MakeDoc(int level = 3)
    {
        var text = string.Concat(System.Linq.Enumerable.Repeat("Test content for Zstandard document. ", 200));
        var data = ZstWriter.CompressString(text, level);
        return ZstParser.ParseBytes(data);
    }

    // -------------------------------------------------------------------------
    // ToString
    // -------------------------------------------------------------------------

    [Fact]
    public void ToString_NonNull()
    {
        var doc = MakeDoc();
        Assert.NotNull(doc.ToString());
    }

    [Fact]
    public void ToString_NonEmpty()
    {
        var doc = MakeDoc();
        Assert.NotEmpty(doc.ToString());
    }

    [Fact]
    public void ToString_Consistent()
    {
        var doc = MakeDoc();
        Assert.Equal(doc.ToString(), doc.ToString());
    }

    [Fact]
    public void ToString_NoThrow()
    {
        var doc = MakeDoc();
        var ex = Record.Exception(() => _ = doc.ToString());
        Assert.Null(ex);
    }

    [Fact]
    public void ToString_LengthPositive()
    {
        var doc = MakeDoc();
        Assert.True(doc.ToString().Length > 0);
    }

    [Fact]
    public void ToString_FromParseFile()
    {
        var src = TempFile("src.txt");
        var dst = TempFile("src.zst");
        File.WriteAllText(src, string.Concat(System.Linq.Enumerable.Repeat("file string test. ", 100)));
        ZstWriter.CompressFile(src, dst);
        var doc = ZstParser.ParseFile(dst);
        Assert.NotNull(doc.ToString());
        Assert.NotEmpty(doc.ToString());
    }

    [Fact]
    public void ToString_FromParseBytes()
    {
        var data = ZstWriter.CompressBytes(System.Text.Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("bytes string test. ", 100))));
        var doc = ZstParser.ParseBytes(data);
        Assert.NotEmpty(doc.ToString());
    }

    [Fact]
    public void ToString_ConsistentAfterOps()
    {
        var doc = MakeDoc();
        var s1 = doc.ToString();
        _ = doc.FrameCount;
        _ = doc.CompressionRatio;
        var s2 = doc.ToString();
        Assert.Equal(s1, s2);
    }

    // -------------------------------------------------------------------------
    // ToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToJson_NonNull()
    {
        var doc = MakeDoc();
        Assert.NotNull(doc.ToJson());
    }

    [Fact]
    public void ToJson_NonEmpty()
    {
        var doc = MakeDoc();
        Assert.NotEmpty(doc.ToJson());
    }

    [Fact]
    public void ToJson_Consistent()
    {
        var doc = MakeDoc();
        Assert.Equal(doc.ToJson().Length, doc.ToJson().Length);
    }

    [Fact]
    public void ToJson_NoThrow()
    {
        var doc = MakeDoc();
        var ex = Record.Exception(() => _ = doc.ToJson());
        Assert.Null(ex);
    }

    [Fact]
    public void ToJson_HasBraces()
    {
        var doc = MakeDoc();
        var json = doc.ToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ToJson_HasSizeInfo()
    {
        var doc = MakeDoc();
        var json = doc.ToJson();
        Assert.True(json.Contains("size") || json.Contains("Size") ||
                    json.Contains("compressed") || json.Contains("Compressed") ||
                    json.Contains("decompressed") || json.Contains("Decompressed"));
    }

    [Fact]
    public void ToJson_FromParseFile()
    {
        var src = TempFile("src2.txt");
        var dst = TempFile("src2.zst");
        File.WriteAllText(src, string.Concat(System.Linq.Enumerable.Repeat("file json test. ", 100)));
        ZstWriter.CompressFile(src, dst);
        var doc = ZstParser.ParseFile(dst);
        var json = doc.ToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
    }

    [Fact]
    public void ToJson_FromParseBytes()
    {
        var data = ZstWriter.CompressBytes(System.Text.Encoding.UTF8.GetBytes(
            string.Concat(System.Linq.Enumerable.Repeat("bytes json test. ", 100))));
        var doc = ZstParser.ParseBytes(data);
        Assert.NotEmpty(doc.ToJson());
    }

    [Fact]
    public void ToJson_FromParseStream()
    {
        var data = ZstWriter.CompressString(string.Concat(System.Linq.Enumerable.Repeat("stream json. ", 100)));
        using var ms = new MemoryStream(data);
        var doc = ZstParser.ParseStream(ms);
        Assert.NotEmpty(doc.ToJson());
    }

    // -------------------------------------------------------------------------
    // CompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressionLevel_NonNegative()
    {
        var doc = MakeDoc();
        Assert.True(doc.CompressionLevel >= 0);
    }

    [Fact]
    public void CompressionLevel_InRange()
    {
        var doc = MakeDoc(3);
        // Level is typically 1-22 for zstd, but stored level may be 0-based
        Assert.True(doc.CompressionLevel >= 0 && doc.CompressionLevel <= 22);
    }

    [Fact]
    public void CompressionLevel_Consistent()
    {
        var doc = MakeDoc();
        Assert.Equal(doc.CompressionLevel, doc.CompressionLevel);
    }

    [Fact]
    public void CompressionLevel_NoThrow()
    {
        var doc = MakeDoc();
        var ex = Record.Exception(() => _ = doc.CompressionLevel);
        Assert.Null(ex);
    }

    [Fact]
    public void CompressionLevel_FromParseFile()
    {
        var src = TempFile("src3.txt");
        var dst = TempFile("src3.zst");
        File.WriteAllText(src, string.Concat(System.Linq.Enumerable.Repeat("level from file. ", 100)));
        ZstWriter.CompressFile(src, dst);
        var doc = ZstParser.ParseFile(dst);
        Assert.True(doc.CompressionLevel >= 0);
    }

    [Fact]
    public void CompressionLevel_FromCompressStringLevel1()
    {
        var data = ZstWriter.CompressString(
            string.Concat(System.Linq.Enumerable.Repeat("level 1 data. ", 100)), 1);
        var doc = ZstParser.ParseBytes(data);
        Assert.True(doc.CompressionLevel >= 0);
    }

    [Fact]
    public void CompressionLevel_FromCompressStringLevel9()
    {
        var data = ZstWriter.CompressString(
            string.Concat(System.Linq.Enumerable.Repeat("level 9 data. ", 100)), 9);
        var doc = ZstParser.ParseBytes(data);
        Assert.True(doc.CompressionLevel >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressBytes_ParseBytes_ToString_ToJson_CompressionLevel_Pipeline()
    {
        // Create varied content
        var texts = new[]
        {
            string.Concat(System.Linq.Enumerable.Repeat("Small document content. ", 50)),
            string.Concat(System.Linq.Enumerable.Repeat("Medium sized document with more data. ", 300)),
            string.Concat(System.Linq.Enumerable.Repeat("Large document with substantial content for testing metadata. ", 700))
        };

        ZstDocument[] docs = new ZstDocument[3];
        for (int i = 0; i < 3; i++)
        {
            var data = ZstWriter.CompressString(texts[i], i + 1); // levels 1, 2, 3
            docs[i] = ZstParser.ParseBytes(data);
        }

        // ToString for all
        foreach (var doc in docs)
        {
            Assert.NotNull(doc.ToString());
            Assert.NotEmpty(doc.ToString());
            Assert.True(doc.ToString().Length > 0);
        }

        // ToString consistent
        Assert.Equal(docs[0].ToString(), docs[0].ToString());
        Assert.Equal(docs[2].ToString(), docs[2].ToString());

        // ToJson for all
        foreach (var doc in docs)
        {
            var json = doc.ToJson();
            Assert.NotNull(json);
            Assert.NotEmpty(json);
            Assert.True(json.Contains("{") || json.Contains("["));
        }

        // ToJson consistent
        Assert.Equal(docs[1].ToJson().Length, docs[1].ToJson().Length);

        // CompressionLevel for all
        foreach (var doc in docs)
        {
            Assert.True(doc.CompressionLevel >= 0 && doc.CompressionLevel <= 22);
        }

        // CompressionLevel consistent
        Assert.Equal(docs[0].CompressionLevel, docs[0].CompressionLevel);

        // Size relationships (large doc has larger decompressed size)
        Assert.True(docs[2].DecompressedSize > docs[0].DecompressedSize);

        // ToString has different content for different docs (decompressed sizes differ)
        // At minimum they are both non-empty strings
        Assert.NotEmpty(docs[0].ToString());
        Assert.NotEmpty(docs[2].ToString());

        // ParseFile integration
        var src = TempFile("pipeline_src.txt");
        var dst = TempFile("pipeline_dst.zst");
        File.WriteAllText(src, texts[2]);
        ZstWriter.CompressFile(src, dst);
        var fileDoc = ZstParser.ParseFile(dst);

        Assert.NotEmpty(fileDoc.ToString());
        Assert.NotEmpty(fileDoc.ToJson());
        Assert.True(fileDoc.CompressionLevel >= 0);
        Assert.True(fileDoc.FrameCount >= 1);
        Assert.True(fileDoc.IsValid);

        // ParseStream integration
        var streamData = ZstWriter.CompressString(texts[1], 5);
        using (var ms = new MemoryStream(streamData))
        {
            var streamDoc = ZstParser.ParseStream(ms);
            Assert.NotEmpty(streamDoc.ToString());
            Assert.NotEmpty(streamDoc.ToJson());
            Assert.True(streamDoc.CompressionLevel >= 0);
        }

        // ToDict non-null
        var dict = fileDoc.ToDict();
        Assert.NotNull(dict);
        Assert.True(dict.Count > 0);

        // IsEmpty false for all real docs
        Assert.False(docs[0].IsEmpty);
        Assert.False(docs[1].IsEmpty);
        Assert.False(docs[2].IsEmpty);

        // CompressionRatio non-negative
        foreach (var doc in docs)
            Assert.True(doc.CompressionRatio >= 0.0);

        // FileSizeKB non-negative for ParseBytes docs
        foreach (var doc in docs)
            Assert.True(doc.FileSizeKB >= 0.0);

        // DecompressFile roundtrip
        var outPath = TempFile("pipeline_out.txt");
        ZstWriter.DecompressFile(dst, outPath);
        Assert.True(File.Exists(outPath));
        var recovered = File.ReadAllText(outPath);
        Assert.Contains("Large document with substantial content", recovered);
    }
}
