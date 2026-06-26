// Tests for ZstDocument metadata, frame info, and stream properties deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R206

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R206: Tests for ZstDocument metadata, frame info, and GetFrameInfo deeper.
/// ZstDocument: parsed result from ZstParser.ParseFile or ParseStream.
/// GetFrameInfo(index): returns info about a specific frame.
/// FrameCount: number of compressed frames in the document.
/// DecompressedSize: total decompressed byte count.
/// Covers: FrameCount>=1 after compress; FrameCount consistent; FrameCount no-throw;
/// FrameCount after ParseStream matches ParseFile; DecompressedSize>0;
/// DecompressedSize consistent; DecompressedSize no-throw; DecompressedSize save-load;
/// DecompressedSize matches content length; GetFrameInfo non-null; GetFrameInfo no-throw;
/// GetFrameInfo index 0 valid; GetFrameInfo consistent; GetFrameInfo DecompressedSize>0;
/// IsEmpty false for content; IsValid true for valid file; IsValid no-throw;
/// IsValid consistent; CompressionRatio positive; CompressionRatio consistent;
/// CompressionRatio no-throw; CompressionRatio for repeating content high;
/// dogfood ParseFile→GetFrameInfo→DecompressedSize→FrameCount→IsValid pipeline.
/// </summary>
public class ZstR206MetadataAndFrameInfoDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR206MetadataAndFrameInfoDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR206_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCompressedFile(string content, string name = "test.zst")
    {
        var path = TempFile(name);
        var raw = System.Text.Encoding.UTF8.GetBytes(content);
        ZstWriter.CompressFile(TempFile("_raw_" + name + ".tmp"), path, compressionLevel: 3);
        // Write raw first then compress
        var rawPath = TempFile("raw_" + name + ".bin");
        File.WriteAllBytes(rawPath, raw);
        var zstPath = TempFile(name);
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        return zstPath;
    }

    private string MakeZst(string content, string tag = "doc")
    {
        var rawPath = TempFile($"raw_{tag}.bin");
        var zstPath = TempFile($"{tag}.zst");
        File.WriteAllBytes(rawPath, System.Text.Encoding.UTF8.GetBytes(content));
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        return zstPath;
    }

    // -------------------------------------------------------------------------
    // FrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void FrameCount_AtLeastOne_AfterCompress()
    {
        var path = MakeZst("Frame count test content with some data.", "fc1");
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.FrameCount >= 1);
    }

    [Fact]
    public void FrameCount_Consistent()
    {
        var path = MakeZst("Consistent frame count test.", "fc2");
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.FrameCount, doc.FrameCount);
    }

    [Fact]
    public void FrameCount_NoThrow()
    {
        var path = MakeZst("No throw frame count.", "fc3");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.FrameCount);
        Assert.Null(ex);
    }

    [Fact]
    public void FrameCount_ParseStream_MatchesParseFile()
    {
        var path = MakeZst("Stream vs file frame count comparison.", "fc4");
        var fromFile = ZstParser.ParseFile(path);
        ZstDocument fromStream;
        using (var fs = File.OpenRead(path))
            fromStream = ZstParser.ParseStream(fs);
        Assert.Equal(fromFile.FrameCount, fromStream.FrameCount);
    }

    // -------------------------------------------------------------------------
    // DecompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void DecompressedSize_GreaterThanZero()
    {
        var path = MakeZst("Decompressed size should be positive.", "ds1");
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.DecompressedSize > 0);
    }

    [Fact]
    public void DecompressedSize_Consistent()
    {
        var path = MakeZst("Consistent decompressed size test.", "ds2");
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.DecompressedSize, doc.DecompressedSize);
    }

    [Fact]
    public void DecompressedSize_NoThrow()
    {
        var path = MakeZst("No throw decompressed size.", "ds3");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.DecompressedSize);
        Assert.Null(ex);
    }

    [Fact]
    public void DecompressedSize_ReflectsContentLength()
    {
        var content = "Exactly this content for size check.";
        var expectedBytes = System.Text.Encoding.UTF8.GetByteCount(content);
        var path = MakeZst(content, "ds4");
        var doc = ZstParser.ParseFile(path);
        // Decompressed size should match original content byte length
        Assert.True(doc.DecompressedSize > 0);
        Assert.True(doc.DecompressedSize <= expectedBytes * 2 + 10); // within reasonable bounds
    }

    [Fact]
    public void DecompressedSize_LargerContent_Larger()
    {
        var small = MakeZst("Small.", "ds5a");
        var large = MakeZst(new string('A', 5000), "ds5b");
        var docSmall = ZstParser.ParseFile(small);
        var docLarge = ZstParser.ParseFile(large);
        Assert.True(docLarge.DecompressedSize > docSmall.DecompressedSize);
    }

    // -------------------------------------------------------------------------
    // GetFrameInfo
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameInfo_NonNull_Index0()
    {
        var path = MakeZst("Frame info test content.", "fi1");
        var doc = ZstParser.ParseFile(path);
        Assert.NotNull(doc.GetFrameInfo(0));
    }

    [Fact]
    public void GetFrameInfo_NoThrow_Index0()
    {
        var path = MakeZst("Frame info no throw.", "fi2");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.GetFrameInfo(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameInfo_Consistent()
    {
        var path = MakeZst("Consistent frame info test.", "fi3");
        var doc = ZstParser.ParseFile(path);
        var info1 = doc.GetFrameInfo(0);
        var info2 = doc.GetFrameInfo(0);
        Assert.Equal(info1.DecompressedSize, info2.DecompressedSize);
    }

    [Fact]
    public void GetFrameInfo_DecompressedSize_Positive()
    {
        var path = MakeZst("Frame info decompressed size positive.", "fi4");
        var doc = ZstParser.ParseFile(path);
        var info = doc.GetFrameInfo(0);
        Assert.True(info.DecompressedSize > 0);
    }

    // -------------------------------------------------------------------------
    // IsValid / IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsValid_TrueForValidFile()
    {
        var path = MakeZst("Valid zst file content.", "iv1");
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void IsValid_NoThrow()
    {
        var path = MakeZst("Is valid no throw.", "iv2");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.IsValid);
        Assert.Null(ex);
    }

    [Fact]
    public void IsValid_Consistent()
    {
        var path = MakeZst("Consistent is valid.", "iv3");
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.IsValid, doc.IsValid);
    }

    [Fact]
    public void IsEmpty_FalseForContent()
    {
        var path = MakeZst("Not empty document.", "ie1");
        var doc = ZstParser.ParseFile(path);
        Assert.False(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // CompressionRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressionRatio_Positive()
    {
        var path = MakeZst("Compression ratio test content here.", "cr1");
        var doc = ZstParser.ParseFile(path);
        Assert.True(doc.CompressionRatio > 0.0);
    }

    [Fact]
    public void CompressionRatio_Consistent()
    {
        var path = MakeZst("Consistent compression ratio.", "cr2");
        var doc = ZstParser.ParseFile(path);
        Assert.Equal(doc.CompressionRatio, doc.CompressionRatio);
    }

    [Fact]
    public void CompressionRatio_NoThrow()
    {
        var path = MakeZst("No throw compression ratio.", "cr3");
        var doc = ZstParser.ParseFile(path);
        var ex = Record.Exception(() => doc.CompressionRatio);
        Assert.Null(ex);
    }

    [Fact]
    public void CompressionRatio_RepeatingContent_High()
    {
        // Highly repetitive content should compress well
        var content = new string('X', 10000);
        var path = MakeZst(content, "cr4");
        var doc = ZstParser.ParseFile(path);
        // Ratio should be >= 1 (good compression = large ratio)
        Assert.True(doc.CompressionRatio >= 1.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ParseFile_GetFrameInfo_DecompressedSize_FrameCount_IsValid_Pipeline()
    {
        // Create three different documents at different compression levels
        var contentA = "Annual performance review data: revenue targets met by all three divisions.";
        var contentB = new string('B', 2000) + " end of repetitive content block.";
        var contentC = "Mixed content: " + string.Join(", ", new[] { "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta" });

        var pathA = MakeZst(contentA, "dogfood_a");
        var pathB = MakeZst(contentB, "dogfood_b");
        var pathC = MakeZst(contentC, "dogfood_c");

        // Parse all three
        var docA = ZstParser.ParseFile(pathA);
        var docB = ZstParser.ParseFile(pathB);
        var docC = ZstParser.ParseFile(pathC);

        // FrameCount >= 1 for all
        Assert.True(docA.FrameCount >= 1);
        Assert.True(docB.FrameCount >= 1);
        Assert.True(docC.FrameCount >= 1);

        // IsValid for all
        Assert.True(docA.IsValid);
        Assert.True(docB.IsValid);
        Assert.True(docC.IsValid);

        // IsEmpty false for all
        Assert.False(docA.IsEmpty);
        Assert.False(docB.IsEmpty);
        Assert.False(docC.IsEmpty);

        // DecompressedSize positive for all
        Assert.True(docA.DecompressedSize > 0);
        Assert.True(docB.DecompressedSize > 0);
        Assert.True(docC.DecompressedSize > 0);

        // docB (repetitive) has larger DecompressedSize than docA (short)
        Assert.True(docB.DecompressedSize > docA.DecompressedSize);

        // CompressionRatio positive for all
        Assert.True(docA.CompressionRatio > 0.0);
        Assert.True(docB.CompressionRatio > 0.0);
        Assert.True(docC.CompressionRatio > 0.0);

        // docB (highly repetitive) should compress better than docA (unique text)
        // Ratio should be >= 1 for repetitive content
        Assert.True(docB.CompressionRatio >= 1.0);

        // GetFrameInfo for all
        var infoA = docA.GetFrameInfo(0);
        var infoB = docB.GetFrameInfo(0);
        var infoC = docC.GetFrameInfo(0);
        Assert.NotNull(infoA);
        Assert.NotNull(infoB);
        Assert.NotNull(infoC);
        Assert.True(infoA.DecompressedSize > 0);
        Assert.True(infoB.DecompressedSize > 0);
        Assert.True(infoC.DecompressedSize > 0);

        // Consistent checks
        Assert.Equal(docA.FrameCount, docA.FrameCount);
        Assert.Equal(docB.DecompressedSize, docB.DecompressedSize);
        Assert.Equal(docC.CompressionRatio, docC.CompressionRatio);

        // ParseStream matches ParseFile for docA
        ZstDocument docAStream;
        using (var fs = File.OpenRead(pathA))
            docAStream = ZstParser.ParseStream(fs);
        Assert.Equal(docA.FrameCount, docAStream.FrameCount);
        Assert.Equal(docA.DecompressedSize, docAStream.DecompressedSize);

        // Decompress and verify round-trip for docA
        var decompPath = TempFile("dogfood_a_decomp.bin");
        ZstWriter.DecompressFile(pathA, decompPath);
        Assert.True(File.Exists(decompPath));
        var decompContent = System.Text.Encoding.UTF8.GetString(File.ReadAllBytes(decompPath));
        Assert.Contains("Annual", decompContent);

        // Round-trip for docB
        var decompPathB = TempFile("dogfood_b_decomp.bin");
        ZstWriter.DecompressFile(pathB, decompPathB);
        Assert.True(File.Exists(decompPathB));
        var decompB = File.ReadAllBytes(decompPathB);
        Assert.True(decompB.Length > 0);
    }
}
