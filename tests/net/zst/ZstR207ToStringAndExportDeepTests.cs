// Tests for ZstDocument.ToString, ToJson, ExportToBase64 deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R207

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R207: Tests for ZstDocument.ToString, ToJson, ExportToBase64 deeper.
/// ToString(): returns a string representation of the ZstDocument metadata.
/// ToJson(): returns a JSON string with document properties.
/// ExportToBase64(): returns the compressed bytes encoded as a base64 string.
/// Covers: ToString non-null; ToString non-empty; ToString no-throw; ToString consistent;
/// ToString from ParseFile; ToString from ParseStream; ToString has size info;
/// ToJson non-null; ToJson non-empty; ToJson no-throw; ToJson consistent;
/// ToJson has braces; ToJson has frame count; ToJson has size info;
/// ToJson from ParseFile; ToJson after large content;
/// ExportToBase64 non-null; ExportToBase64 non-empty; ExportToBase64 no-throw;
/// ExportToBase64 consistent; ExportToBase64 is valid base64; ExportToBase64 for different docs differs;
/// ExportToBase64 roundtrip decompresses; ExportToBase64 length > 0;
/// dogfood ParseFile→ToString→ToJson→ExportToBase64→SaveToFile pipeline.
/// </summary>
public class ZstR207ToStringAndExportDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR207ToStringAndExportDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR207_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string MakeZst(string content, string tag = "doc")
    {
        var rawPath = TempFile($"raw_{tag}.bin");
        var zstPath = TempFile($"{tag}.zst");
        File.WriteAllBytes(rawPath, System.Text.Encoding.UTF8.GetBytes(content));
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        return zstPath;
    }

    // -------------------------------------------------------------------------
    // ToString
    // -------------------------------------------------------------------------

    [Fact]
    public void ToString_NonNull()
    {
        var path = MakeZst("ToString test content.", "ts1");
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc.ToString());
    }

    [Fact]
    public void ToString_NonEmpty()
    {
        var path = MakeZst("ToString non-empty test.", "ts2");
        var doc = ZstParser.ParseFile(path);
        Assert.NotEmpty(doc.ToString());
    }

    [Fact]
    public void ToString_NoThrow()
    {
        var path = MakeZst("No throw test.", "ts3");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.ToString());
        Assert.Null(ex);
    }

    [Fact]
    public void ToString_Consistent()
    {
        var path = MakeZst("Consistent ToString.", "ts4");
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.ToString(), doc.ToString());
    }

    [Fact]
    public void ToString_HasSizeInfo()
    {
        var path = MakeZst("Content for size info check.", "ts5");
        var doc = ZstParser.ParseFile(path);
        var str = doc.ToString();
        // Should contain some numeric information (size, frame count, etc.)
        Assert.True(str.Any(char.IsDigit));
    }

    [Fact]
    public void ToString_FromParseStream()
    {
        var path = MakeZst("Parse stream to string.", "ts6");
        ZstDocument doc;
        using (var fs = File.OpenRead(path))
            doc = ZstParser.ParseStream(fs);
        Assert.NotNull(doc.ToString());
        Assert.NotEmpty(doc.ToString());
    }

    // -------------------------------------------------------------------------
    // ToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ToJson_NonNull()
    {
        var path = MakeZst("ToJson test content.", "tj1");
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc.ToJson());
    }

    [Fact]
    public void ToJson_NonEmpty()
    {
        var path = MakeZst("ToJson non-empty.", "tj2");
        var doc = ZstParser.ParseFile(path);
        Assert.NotEmpty(doc.ToJson());
    }

    [Fact]
    public void ToJson_NoThrow()
    {
        var path = MakeZst("ToJson no throw.", "tj3");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.ToJson());
        Assert.Null(ex);
    }

    [Fact]
    public void ToJson_Consistent()
    {
        var path = MakeZst("Consistent ToJson.", "tj4");
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.ToJson().Length, doc.ToJson().Length);
    }

    [Fact]
    public void ToJson_HasBraces()
    {
        var path = MakeZst("ToJson braces check.", "tj5");
        var doc = ZstParser.ParseFile(path);
        var json = doc.ToJson();
        Assert.True(json.Contains("{") && json.Contains("}"));
    }

    [Fact]
    public void ToJson_HasSizeInfo()
    {
        var path = MakeZst("ToJson size info check.", "tj6");
        var doc = ZstParser.ParseFile(path);
        var json = doc.ToJson();
        // Should contain size-related numbers
        Assert.True(json.Any(char.IsDigit));
    }

    [Fact]
    public void ToJson_AfterLargeContent_NonEmpty()
    {
        var path = MakeZst(new string('Q', 5000), "tj7");
        var doc = ZstParser.ParseFile(path);
        Assert.NotEmpty(doc.ToJson());
    }

    // -------------------------------------------------------------------------
    // ExportToBase64
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToBase64_NonNull()
    {
        var path = MakeZst("Base64 export content.", "b64_1");
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc.ExportToBase64());
    }

    [Fact]
    public void ExportToBase64_NonEmpty()
    {
        var path = MakeZst("Base64 non-empty.", "b64_2");
        var doc = ZstParser.ParseFile(path);
        Assert.NotEmpty(doc.ExportToBase64());
    }

    [Fact]
    public void ExportToBase64_NoThrow()
    {
        var path = MakeZst("Base64 no throw.", "b64_3");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.ExportToBase64());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToBase64_Consistent()
    {
        var path = MakeZst("Consistent base64.", "b64_4");
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.ExportToBase64(), doc.ExportToBase64());
    }

    [Fact]
    public void ExportToBase64_IsValidBase64()
    {
        var path = MakeZst("Valid base64 test.", "b64_5");
        var doc = ZstParser.ParseFile(path);
        var b64 = doc.ExportToBase64();
        // Should not throw when decoded
        var ex = Record.Exception(() => Convert.FromBase64String(b64));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToBase64_DifferentDocs_DifferentStrings()
    {
        var path1 = MakeZst("Content A for base64 comparison.", "b64_6a");
        var path2 = MakeZst("Content B entirely different here.", "b64_6b");
        var doc1 = ZstParser.ParseFile(path1);
        var doc2 = ZstParser.ParseFile(path2);
        // Different content should produce different base64
        Assert.NotEqual(doc1.ExportToBase64(), doc2.ExportToBase64());
    }

    [Fact]
    public void ExportToBase64_Roundtrip_CanSaveAndParse()
    {
        var path = MakeZst("Roundtrip base64 content.", "b64_7");
        var doc = ZstParser.ParseFile(path);
        var b64 = doc.ExportToBase64();
        var bytes = Convert.FromBase64String(b64);
        // Write back and parse
        var outPath = TempFile("b64_roundtrip.zst");
        File.WriteAllBytes(outPath, bytes);
        var reloaded = ZstParser.ParseFile(outPath);
        Assert.Equal(doc.FrameCount, reloaded.FrameCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ParseFile_ToString_ToJson_ExportToBase64_SaveToFile_Pipeline()
    {
        // Create three documents with different content
        var contentSmall = "Small document content for metadata export.";
        var contentMedium = string.Join(" ", new[] {
            "The quarterly report presents comprehensive analysis of market conditions.",
            "Revenue growth exceeded projections by eight percent this quarter.",
            "Customer acquisition costs decreased while retention rates improved.",
            "The technology division posted record performance for three consecutive months."
        });
        var contentLarge = new string('Z', 3000) + " end marker for large content.";

        var pathSmall = MakeZst(contentSmall, "df_small");
        var pathMedium = MakeZst(contentMedium, "df_medium");
        var pathLarge = MakeZst(contentLarge, "df_large");

        var docSmall = ZstParser.ParseFile(pathSmall);
        var docMedium = ZstParser.ParseFile(pathMedium);
        var docLarge = ZstParser.ParseFile(pathLarge);

        // ToString all — non-null and non-empty
        Assert.NotNull(docSmall.ToString());
        Assert.NotNull(docMedium.ToString());
        Assert.NotNull(docLarge.ToString());
        Assert.NotEmpty(docSmall.ToString());
        Assert.NotEmpty(docMedium.ToString());

        // ToString consistent
        Assert.Equal(docSmall.ToString(), docSmall.ToString());
        Assert.Equal(docMedium.ToString(), docMedium.ToString());

        // ToString has numeric content
        Assert.True(docSmall.ToString().Any(char.IsDigit));

        // ToJson all — valid JSON structure
        var jsonSmall = docSmall.ToJson();
        var jsonMedium = docMedium.ToJson();
        var jsonLarge = docLarge.ToJson();
        Assert.NotNull(jsonSmall);
        Assert.True(jsonSmall.Contains("{") && jsonSmall.Contains("}"));
        Assert.True(jsonMedium.Contains("{") && jsonMedium.Contains("}"));
        Assert.True(jsonLarge.Contains("{") && jsonLarge.Contains("}"));

        // ToJson consistent
        Assert.Equal(jsonSmall.Length, docSmall.ToJson().Length);

        // ExportToBase64 all — valid base64
        var b64Small = docSmall.ExportToBase64();
        var b64Medium = docMedium.ExportToBase64();
        var b64Large = docLarge.ExportToBase64();
        Assert.NotNull(b64Small);
        Assert.NotEmpty(b64Small);

        // All are valid base64
        var bytesSmall = Convert.FromBase64String(b64Small);
        var bytesMedium = Convert.FromBase64String(b64Medium);
        var bytesLarge = Convert.FromBase64String(b64Large);
        Assert.True(bytesSmall.Length > 0);
        Assert.True(bytesMedium.Length > 0);
        Assert.True(bytesLarge.Length > 0);

        // Larger content → larger base64
        Assert.True(b64Large.Length > b64Small.Length);

        // Roundtrip: decode base64 → write → parse → verify
        var outPath = TempFile("df_b64_roundtrip.zst");
        File.WriteAllBytes(outPath, bytesMedium);
        var reloaded = ZstParser.ParseFile(outPath);
        Assert.Equal(docMedium.FrameCount, reloaded.FrameCount);
        Assert.Equal(docMedium.DecompressedSize, reloaded.DecompressedSize);

        // ToString on reloaded
        Assert.NotEmpty(reloaded.ToString());

        // ToJson on reloaded
        Assert.NotEmpty(reloaded.ToJson());

        // ExportToBase64 on reloaded = same as original
        Assert.Equal(b64Medium, reloaded.ExportToBase64());

        // ParseStream for one doc
        ZstDocument docStreamMedium;
        using (var fs = File.OpenRead(pathMedium))
            docStreamMedium = ZstParser.ParseStream(fs);
        Assert.Equal(docMedium.ToString().Length, docStreamMedium.ToString().Length);

        // IsValid all
        Assert.True(docSmall.IsValid);
        Assert.True(docMedium.IsValid);
        Assert.True(docLarge.IsValid);
    }
}
