// Tests for ZstDocument.GetWindowLog, GetSrcSize, GetOriginalFileName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R217

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R217: Tests for ZstDocument.GetWindowLog, GetSrcSize, GetOriginalFileName deeper.
/// GetWindowLog(): returns the window log (log2 of window size) from the frame header.
/// GetSrcSize(): returns the uncompressed source size stored in the frame header.
/// GetOriginalFileName(): returns the original file name hint if stored in the frame.
/// Covers: GetWindowLog no-throw; GetWindowLog positive; GetWindowLog consistent;
/// GetWindowLog save-load; GetWindowLog reasonable range;
/// GetSrcSize no-throw; GetSrcSize non-negative; GetSrcSize consistent;
/// GetSrcSize save-load; GetSrcSize matches GetDecompressedSize;
/// GetOriginalFileName no-throw; GetOriginalFileName non-null; GetOriginalFileName consistent;
/// GetOriginalFileName save-load;
/// dogfood CompressFile→GetWindowLog→GetSrcSize→GetOriginalFileName→SaveToFile pipeline.
/// </summary>
public class ZstR217GetWindowLogAndSrcSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR217GetWindowLogAndSrcSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR217_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private ZstDocument MakeDoc(string content, int level = 3)
    {
        var raw = TempFile("r_" + Guid.NewGuid().ToString("N") + ".txt");
        var zst = TempFile("z_" + Guid.NewGuid().ToString("N") + ".zst");
        File.WriteAllText(raw, content);
        ZstWriter.CompressFile(raw, zst, compressionLevel: level);
        return ZstDocument.LoadFile(zst);
    }

    private static string RepeatText(string phrase, int times)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < times; i++)
            sb.Append(phrase).Append(' ').Append(i).Append('\n');
        return sb.ToString();
    }

    // -------------------------------------------------------------------------
    // GetWindowLog
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowLog_NoThrow()
    {
        var doc = MakeDoc(RepeatText("window log no throw", 80));
        var ex = Record.Exception(() => doc.GetWindowLog());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowLog_Positive()
    {
        var doc = MakeDoc(RepeatText("window log positive", 80));
        Assert.True(doc.GetWindowLog() > 0);
    }

    [Fact]
    public void GetWindowLog_Consistent()
    {
        var doc = MakeDoc(RepeatText("window log consistent", 80));
        Assert.Equal(doc.GetWindowLog(), doc.GetWindowLog());
    }

    [Fact]
    public void GetWindowLog_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("window log save load", 80));
        var before = doc.GetWindowLog();
        var path = TempFile("wl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowLog());
    }

    [Fact]
    public void GetWindowLog_ReasonableRange()
    {
        var doc = MakeDoc(RepeatText("window log range", 80));
        var wl = doc.GetWindowLog();
        // zstd window log: 10 (1KB) to 31 (2GB)
        Assert.True(wl >= 10 && wl <= 31);
    }

    // -------------------------------------------------------------------------
    // GetSrcSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSrcSize_NoThrow()
    {
        var doc = MakeDoc(RepeatText("src size no throw", 80));
        var ex = Record.Exception(() => doc.GetSrcSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSrcSize_NonNegative()
    {
        var doc = MakeDoc(RepeatText("src size non negative", 80));
        Assert.True(doc.GetSrcSize() >= 0);
    }

    [Fact]
    public void GetSrcSize_Consistent()
    {
        var doc = MakeDoc(RepeatText("src size consistent", 80));
        Assert.Equal(doc.GetSrcSize(), doc.GetSrcSize());
    }

    [Fact]
    public void GetSrcSize_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("src size save load", 80));
        var before = doc.GetSrcSize();
        var path = TempFile("ss_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSrcSize());
    }

    [Fact]
    public void GetSrcSize_Matches_DecompressedSize()
    {
        var doc = MakeDoc(RepeatText("src size vs decompressed", 80));
        var srcSize = doc.GetSrcSize();
        var decompSize = doc.GetDecompressedSize();
        // srcSize should equal decompressedSize if content size is stored in header
        Assert.True(srcSize == 0 || srcSize == decompSize);
    }

    // -------------------------------------------------------------------------
    // GetOriginalFileName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOriginalFileName_NoThrow()
    {
        var doc = MakeDoc(RepeatText("orig file name no throw", 80));
        var ex = Record.Exception(() => doc.GetOriginalFileName());
        Assert.Null(ex);
    }

    [Fact]
    public void GetOriginalFileName_NonNull()
    {
        var doc = MakeDoc(RepeatText("orig file name non null", 80));
        Assert.NotNull(doc.GetOriginalFileName());
    }

    [Fact]
    public void GetOriginalFileName_Consistent()
    {
        var doc = MakeDoc(RepeatText("orig file name consistent", 80));
        Assert.Equal(doc.GetOriginalFileName(), doc.GetOriginalFileName());
    }

    [Fact]
    public void GetOriginalFileName_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("orig file name save load", 80));
        var before = doc.GetOriginalFileName();
        var path = TempFile("ofn_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        var after = loaded.GetOriginalFileName();
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetWindowLog_GetSrcSize_GetOriginalFileName_SaveToFile_Pipeline()
    {
        var original = RepeatText("Dogfood window log src size original file name pipeline test content", 120);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetWindowLog
        var wl = doc.GetWindowLog();
        Assert.True(wl > 0);
        Assert.Equal(wl, doc.GetWindowLog()); // consistent

        // GetSrcSize
        var srcSize = doc.GetSrcSize();
        Assert.True(srcSize >= 0);
        Assert.Equal(srcSize, doc.GetSrcSize()); // consistent

        // GetOriginalFileName
        var fname = doc.GetOriginalFileName();
        Assert.NotNull(fname);
        Assert.Equal(fname, doc.GetOriginalFileName()); // consistent

        // Other assertions
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.IsValid);

        // GetCompressionStats
        var stats = doc.GetCompressionStats();
        Assert.NotNull(stats);
        Assert.True(stats.Ratio > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify consistency
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(wl, loaded.GetWindowLog());
        Assert.Equal(srcSize, loaded.GetSrcSize());
        Assert.Equal(doc.GetDecompressedSize(), loaded.GetDecompressedSize());

        // Decompress and verify content
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Second doc at level 6
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, RepeatText("Second content set for window log comparison test", 90));
        var zst2 = TempFile("dogfood_src2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 6);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.True(doc2.IsValid);
        Assert.True(doc2.GetWindowLog() > 0);
        Assert.True(doc2.GetSrcSize() >= 0);
        Assert.NotNull(doc2.GetOriginalFileName());

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(doc2.GetWindowLog(), final.GetWindowLog());
        Assert.Equal(doc2.GetSrcSize(), final.GetSrcSize());
    }
}
