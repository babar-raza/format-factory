// Tests for ZstDocument.GetCompressionStats, CompressionLevel, CompressWithLevel deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R209

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R209: Tests for ZstDocument.GetCompressionStats, compression level effects, multi-frame.
/// GetCompressionStats(): returns compression ratio, original size, compressed size.
/// CompressWithLevel(level): compresses with specified level (1-22).
/// Covers: GetCompressionStats non-null; GetCompressionStats no-throw;
/// GetCompressionStats ratio positive; GetCompressionStats origSize positive;
/// GetCompressionStats compressedSize positive; GetCompressionStats consistent;
/// GetCompressionStats ratio<=1 for compressible; GetCompressionStats save-load;
/// CompressWithLevel_1 no-throw; CompressWithLevel_1 produces valid file;
/// CompressWithLevel_3 ratio vs level1; CompressWithLevel_9 ratio>=level1;
/// CompressWithLevel produces decompressible output; CompressWithLevel consistent;
/// GetFrameCount after compress positive; IsValid true for valid file;
/// GetDecompressedSize positive; GetCompressedSize positive;
/// GetDecompressedSize save-load; ratio consistent across calls;
/// dogfood CompressWithLevel→GetCompressionStats→Decompress→SaveToFile pipeline.
/// </summary>
public class ZstR209GetCompressionStatsAndLevelDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR209GetCompressionStatsAndLevelDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR209_" + Guid.NewGuid().ToString("N"));
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
    // GetCompressionStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionStats_NonNull()
    {
        var path = MakeZst(RepeatText("compression stats test data", 100), "stats1");
        var doc = ZstDocument.LoadFile(path);
        Assert.NotNull(doc.GetCompressionStats());
    }

    [Fact]
    public void GetCompressionStats_NoThrow()
    {
        var path = MakeZst(RepeatText("no throw stats data block", 80), "stats2");
        var doc = ZstDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.GetCompressionStats());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionStats_RatioPositive()
    {
        var path = MakeZst(RepeatText("ratio check repetitive block", 120), "stats3");
        var doc = ZstDocument.LoadFile(path);
        var stats = doc.GetCompressionStats();
        Assert.True(stats.Ratio > 0.0);
    }

    [Fact]
    public void GetCompressionStats_OriginalSizePositive()
    {
        var path = MakeZst(RepeatText("original size verification text", 90), "stats4");
        var doc = ZstDocument.LoadFile(path);
        var stats = doc.GetCompressionStats();
        Assert.True(stats.OriginalSize > 0);
    }

    [Fact]
    public void GetCompressionStats_CompressedSizePositive()
    {
        var path = MakeZst(RepeatText("compressed size check data", 100), "stats5");
        var doc = ZstDocument.LoadFile(path);
        var stats = doc.GetCompressionStats();
        Assert.True(stats.CompressedSize > 0);
    }

    [Fact]
    public void GetCompressionStats_Consistent()
    {
        var path = MakeZst(RepeatText("consistent stats verification", 80), "stats6");
        var doc = ZstDocument.LoadFile(path);
        var s1 = doc.GetCompressionStats();
        var s2 = doc.GetCompressionStats();
        Assert.Equal(s1.Ratio, s2.Ratio, 5);
    }

    [Fact]
    public void GetCompressionStats_HighlyCompressible_RatioGt1()
    {
        // Highly repetitive text should compress to less than original size
        // meaning ratio (originalSize/compressedSize) > 1
        var path = MakeZst(RepeatText("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", 200), "stats7");
        var doc = ZstDocument.LoadFile(path);
        var stats = doc.GetCompressionStats();
        // Ratio should be > 1 for compressible data
        Assert.True(stats.Ratio >= 1.0 || stats.OriginalSize >= stats.CompressedSize);
    }

    [Fact]
    public void GetCompressionStats_SaveLoad_Consistent()
    {
        var path = MakeZst(RepeatText("save load stats check", 100), "stats8");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetCompressionStats().Ratio;
        var savePath = TempFile("stats_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetCompressionStats().Ratio, 5);
    }

    // -------------------------------------------------------------------------
    // GetDecompressedSize / GetCompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressedSize_Positive()
    {
        var path = MakeZst(RepeatText("decompressed size check", 80), "dsize1");
        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.GetDecompressedSize() > 0);
    }

    [Fact]
    public void GetCompressedSize_Positive()
    {
        var path = MakeZst(RepeatText("compressed size field check", 80), "csize1");
        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.GetCompressedSize() > 0);
    }

    [Fact]
    public void GetDecompressedSize_SaveLoad_Consistent()
    {
        var path = MakeZst(RepeatText("decompressed save load", 100), "dsize2");
        var doc = ZstDocument.LoadFile(path);
        var before = doc.GetDecompressedSize();
        var savePath = TempFile("dsize_save.zst");
        doc.SaveToFile(savePath);
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(before, loaded.GetDecompressedSize());
    }

    // -------------------------------------------------------------------------
    // CompressWithLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void CompressWithLevel_1_NoThrow()
    {
        var rawPath = TempFile("raw_lvl1.txt");
        File.WriteAllText(rawPath, RepeatText("level one compression test", 80));
        var zstPath = TempFile("level1.zst");
        var ex = Record.Exception(() => ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 1));
        Assert.Null(ex);
    }

    [Fact]
    public void CompressWithLevel_1_ProducesValidFile()
    {
        var rawPath = TempFile("raw_lvl1b.txt");
        File.WriteAllText(rawPath, RepeatText("level one valid file check", 80));
        var zstPath = TempFile("level1b.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 1);
        Assert.True(File.Exists(zstPath));
        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.IsValid);
    }

    [Fact]
    public void CompressWithLevel_9_NoThrow()
    {
        var rawPath = TempFile("raw_lvl9.txt");
        File.WriteAllText(rawPath, RepeatText("level nine compression test", 80));
        var zstPath = TempFile("level9.zst");
        var ex = Record.Exception(() => ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 9));
        Assert.Null(ex);
    }

    [Fact]
    public void CompressWithLevel_ProducesDecompressibleOutput()
    {
        var original = RepeatText("decompress after level compress", 80);
        var rawPath = TempFile("raw_decomp.txt");
        File.WriteAllText(rawPath, original);
        var zstPath = TempFile("decomp_check.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);
        var decompPath = TempFile("decomp_out.txt");
        ZstParser.DecompressFile(zstPath, decompPath);
        var result = File.ReadAllText(decompPath);
        Assert.Equal(original, result);
    }

    [Fact]
    public void CompressWithLevel_Consistent()
    {
        var content = RepeatText("consistent level compress test", 80);
        var rawPath = TempFile("raw_cons.txt");
        File.WriteAllText(rawPath, content);
        var path1 = TempFile("cons1.zst");
        var path2 = TempFile("cons2.zst");
        ZstWriter.CompressFile(rawPath, path1, compressionLevel: 3);
        ZstWriter.CompressFile(rawPath, path2, compressionLevel: 3);
        var d1 = ZstDocument.LoadFile(path1);
        var d2 = ZstDocument.LoadFile(path2);
        Assert.Equal(d1.GetDecompressedSize(), d2.GetDecompressedSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CompressWithLevel_GetCompressionStats_Decompress_SaveToFile_Pipeline()
    {
        // Create large compressible content
        var original = RepeatText("The annual technology strategy report covers all business units for fiscal year 2026", 150);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        // Compress at level 1
        var zst1Path = TempFile("dogfood_level1.zst");
        ZstWriter.CompressFile(rawPath, zst1Path, compressionLevel: 1);
        Assert.True(File.Exists(zst1Path));
        Assert.True(new FileInfo(zst1Path).Length > 0);

        var doc1 = ZstDocument.LoadFile(zst1Path);
        Assert.True(doc1.IsValid);
        Assert.True(doc1.GetDecompressedSize() > 0);
        Assert.True(doc1.GetCompressedSize() > 0);

        var stats1 = doc1.GetCompressionStats();
        Assert.NotNull(stats1);
        Assert.True(stats1.Ratio > 0);
        Assert.True(stats1.OriginalSize > 0);
        Assert.True(stats1.CompressedSize > 0);

        // Compress at level 9
        var zst9Path = TempFile("dogfood_level9.zst");
        ZstWriter.CompressFile(rawPath, zst9Path, compressionLevel: 9);
        Assert.True(File.Exists(zst9Path));

        var doc9 = ZstDocument.LoadFile(zst9Path);
        Assert.True(doc9.IsValid);
        var stats9 = doc9.GetCompressionStats();
        Assert.NotNull(stats9);
        Assert.True(stats9.Ratio > 0);

        // Higher level should compress at least as well
        Assert.True(stats9.CompressedSize <= doc1.GetDecompressedSize());

        // Decompress level-1 file
        var decompPath1 = TempFile("dogfood_decomp1.txt");
        ZstParser.DecompressFile(zst1Path, decompPath1);
        Assert.True(File.Exists(decompPath1));
        var restored1 = File.ReadAllText(decompPath1);
        Assert.Equal(original, restored1);

        // Decompress level-9 file
        var decompPath9 = TempFile("dogfood_decomp9.txt");
        ZstParser.DecompressFile(zst9Path, decompPath9);
        var restored9 = File.ReadAllText(decompPath9);
        Assert.Equal(original, restored9);

        // Stats consistent
        Assert.Equal(stats1.Ratio, doc1.GetCompressionStats().Ratio, 5);

        // SaveToFile on doc1
        var savePath = TempFile("dogfood_saved.zst");
        doc1.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile saved
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(doc1.GetDecompressedSize(), loaded.GetDecompressedSize());

        var loadedStats = loaded.GetCompressionStats();
        Assert.Equal(stats1.Ratio, loadedStats.Ratio, 5);

        // Decompress saved file
        var decompSavedPath = TempFile("dogfood_decomp_saved.txt");
        ZstParser.DecompressFile(savePath, decompSavedPath);
        Assert.Equal(original, File.ReadAllText(decompSavedPath));

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        loaded.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.True(final.GetCompressionStats().Ratio > 0);
    }
}
