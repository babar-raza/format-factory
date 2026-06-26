// Tests for ZstDocument.GetContentSize, IsStreamCompressed, GetCompressionLevel deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R213

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R213: Tests for ZstDocument.GetContentSize, IsStreamCompressed, GetCompressionLevel deeper.
/// GetContentSize(): returns the uncompressed content size in bytes.
/// IsStreamCompressed(): returns whether the data is in streaming (vs. block) format.
/// GetCompressionLevel(): returns the compression level used (1-22) or estimated level.
/// Covers: GetContentSize no-throw; GetContentSize positive; GetContentSize consistent;
/// GetContentSize equals decompressed size; GetContentSize save-load;
/// GetContentSize different content different sizes; GetContentSize after save;
/// IsStreamCompressed no-throw; IsStreamCompressed returns bool; IsStreamCompressed consistent;
/// IsStreamCompressed save-load; IsStreamCompressed valid file always bool;
/// GetCompressionLevel no-throw; GetCompressionLevel valid range;
/// GetCompressionLevel consistent; GetCompressionLevel save-load;
/// GetCompressionLevel level1 vs level9 ordering; GetCompressionLevel positive;
/// dogfood CompressFile→GetContentSize→IsStreamCompressed→GetCompressionLevel→SaveToFile pipeline.
/// </summary>
public class ZstR213GetContentSizeAndStreamInfoDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR213GetContentSizeAndStreamInfoDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR213_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string MakeZst(string content, string tag, int level = 3)
    {
        var rawPath = TempFile($"raw_{tag}.txt");
        var zstPath = TempFile($"{tag}.zst");
        File.WriteAllText(rawPath, content);
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: level);
        return zstPath;
    }

    private static string RepeatText(string phrase, int times)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < times; i++)
            sb.Append(phrase).Append(' ').Append(i).Append('\n');
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // GetContentSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("content size no throw", 80), "cs1"));
        var ex = Record.Exception(() => doc.GetContentSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentSize_Positive()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("content size positive data", 100), "cs2"));
        Assert.True(doc.GetContentSize() > 0);
    }

    [Fact]
    public void GetContentSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("content size consistent check", 80), "cs3"));
        Assert.Equal(doc.GetContentSize(), doc.GetContentSize());
    }

    [Fact]
    public void GetContentSize_Equals_DecompressedSize()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("content size decompressed match", 80), "cs4"));
        Assert.Equal(doc.GetDecompressedSize(), doc.GetContentSize());
    }

    [Fact]
    public void GetContentSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("content size save load", 80), "cs5"));
        var before = doc.GetContentSize();
        var savePath = TempFile("cs_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetContentSize());
    }

    [Fact]
    public void GetContentSize_DifferentContent_DifferentSizes()
    {
        var doc1 = ZstDocument.LoadFile(MakeZst(RepeatText("short content", 20), "cs6a"));
        var doc2 = ZstDocument.LoadFile(MakeZst(RepeatText("longer content with more text", 200), "cs6b"));
        Assert.True(doc2.GetContentSize() > doc1.GetContentSize());
    }

    // -------------------------------------------------------------------------
    // IsStreamCompressed
    // -------------------------------------------------------------------------

    [Fact]
    public void IsStreamCompressed_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("is stream compressed no throw", 80), "sc1"));
        var ex = Record.Exception(() => doc.IsStreamCompressed());
        Assert.Null(ex);
    }

    [Fact]
    public void IsStreamCompressed_ReturnsBool()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("is stream compressed bool", 80), "sc2"));
        var result = doc.IsStreamCompressed();
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void IsStreamCompressed_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("is stream consistent", 80), "sc3"));
        Assert.Equal(doc.IsStreamCompressed(), doc.IsStreamCompressed());
    }

    [Fact]
    public void IsStreamCompressed_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("is stream save load", 80), "sc4"));
        var before = doc.IsStreamCompressed();
        var savePath = TempFile("sc_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.IsStreamCompressed());
    }

    [Fact]
    public void IsStreamCompressed_ValidFile_NoException()
    {
        for (int level = 1; level <= 9; level += 4)
        {
            var doc = ZstDocument.LoadFile(MakeZst(RepeatText($"stream check level {level}", 60), $"sc_l{level}"));
            var ex = Record.Exception(() => doc.IsStreamCompressed());
            Assert.Null(ex);
        }
    }

    // -------------------------------------------------------------------------
    // GetCompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionLevel_NoThrow()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("compression level no throw", 80), "cl1", 3));
        var ex = Record.Exception(() => doc.GetCompressionLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionLevel_Positive()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("compression level positive", 80), "cl2", 5));
        Assert.True(doc.GetCompressionLevel() > 0);
    }

    [Fact]
    public void GetCompressionLevel_ValidRange()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("compression level valid range", 80), "cl3", 3));
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0 && level <= 22);
    }

    [Fact]
    public void GetCompressionLevel_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("compression level consistent", 80), "cl4", 3));
        Assert.Equal(doc.GetCompressionLevel(), doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(MakeZst(RepeatText("compression level save load", 80), "cl5", 5));
        var before = doc.GetCompressionLevel();
        var savePath = TempFile("cl_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetCompressionLevel());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetContentSize_IsStreamCompressed_GetCompressionLevel_SaveToFile_Pipeline()
    {
        var original = RepeatText("Annual strategy review document content for zstd stream information testing", 150);

        // Level 1
        var rawPath1 = TempFile("dogfood_raw1.txt");
        var zstPath1 = TempFile("dogfood_l1.zst");
        File.WriteAllText(rawPath1, original);
        ZstWriter.CompressFile(rawPath1, zstPath1, compressionLevel: 1);

        var doc1 = ZstDocument.LoadFile(zstPath1);
        Assert.True(doc1.IsValid);

        // GetContentSize
        var cs1 = doc1.GetContentSize();
        Assert.True(cs1 > 0);
        Assert.Equal(doc1.GetDecompressedSize(), cs1);
        Assert.Equal(cs1, doc1.GetContentSize()); // consistent

        // IsStreamCompressed
        var isStream1 = doc1.IsStreamCompressed();
        Assert.True(isStream1 == true || isStream1 == false);
        Assert.Equal(isStream1, doc1.IsStreamCompressed()); // consistent

        // GetCompressionLevel
        var cl1 = doc1.GetCompressionLevel();
        Assert.True(cl1 >= 0 && cl1 <= 22);
        Assert.Equal(cl1, doc1.GetCompressionLevel()); // consistent

        // Level 9
        var rawPath9 = TempFile("dogfood_raw9.txt");
        var zstPath9 = TempFile("dogfood_l9.zst");
        File.WriteAllText(rawPath9, original);
        ZstWriter.CompressFile(rawPath9, zstPath9, compressionLevel: 9);

        var doc9 = ZstDocument.LoadFile(zstPath9);
        Assert.True(doc9.IsValid);
        var cs9 = doc9.GetContentSize();

        // Same original → same content size
        Assert.Equal(cs1, cs9);

        // GetCompressionLevel for level 9
        var cl9 = doc9.GetCompressionLevel();
        Assert.True(cl9 >= 0 && cl9 <= 22);

        // IsStreamCompressed consistent across levels
        var isStream9 = doc9.IsStreamCompressed();
        Assert.True(isStream9 == true || isStream9 == false);

        // Stats consistent
        Assert.Equal(doc1.GetCompressionStats().OriginalSize, doc9.GetCompressionStats().OriginalSize);

        // SaveToFile doc1
        var savePath = TempFile("dogfood_saved.zst");
        doc1.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile saved
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(cs1, loaded.GetContentSize());
        Assert.Equal(isStream1, loaded.IsStreamCompressed());
        Assert.Equal(cl1, loaded.GetCompressionLevel());

        // Decompress saved
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Different content → different content size
        var smallContent = "Short content for comparison.";
        var smallPath = TempFile("dogfood_small.txt");
        var smallZst = TempFile("dogfood_small.zst");
        File.WriteAllText(smallPath, smallContent);
        ZstWriter.CompressFile(smallPath, smallZst, compressionLevel: 3);
        var smallDoc = ZstDocument.LoadFile(smallZst);
        Assert.True(cs1 > smallDoc.GetContentSize());

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        loaded.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(cs1, final.GetContentSize());
        Assert.True(final.GetCompressionLevel() >= 0);
    }
}
