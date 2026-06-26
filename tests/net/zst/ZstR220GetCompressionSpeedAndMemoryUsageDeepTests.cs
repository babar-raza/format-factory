// Tests for ZstDocument.GetCompressionSpeed, GetDecompressionSpeed, GetMemoryUsage deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R220

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R220: Tests for ZstDocument.GetCompressionSpeed, GetDecompressionSpeed, GetMemoryUsage deeper.
/// GetCompressionSpeed(): returns an estimate of the compression speed in MB/s or similar unit.
/// GetDecompressionSpeed(): returns an estimate of the decompression speed.
/// GetMemoryUsage(): returns the estimated memory usage during decompression in bytes.
/// Covers: GetCompressionSpeed no-throw; GetCompressionSpeed non-negative; GetCompressionSpeed consistent;
/// GetCompressionSpeed save-load;
/// GetDecompressionSpeed no-throw; GetDecompressionSpeed non-negative; GetDecompressionSpeed consistent;
/// GetDecompressionSpeed save-load;
/// GetMemoryUsage no-throw; GetMemoryUsage positive; GetMemoryUsage consistent;
/// GetMemoryUsage save-load; GetMemoryUsage at-least-decompressed-size;
/// dogfood CompressFile→GetCompressionSpeed→GetDecompressionSpeed→GetMemoryUsage→SaveToFile pipeline.
/// </summary>
public class ZstR220GetCompressionSpeedAndMemoryUsageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR220GetCompressionSpeedAndMemoryUsageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR220_" + Guid.NewGuid().ToString("N"));
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
    // GetCompressionSpeed
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionSpeed_NoThrow()
    {
        var doc = MakeDoc(RepeatText("compression speed no throw", 80));
        var ex = Record.Exception(() => doc.GetCompressionSpeed());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionSpeed_NonNegative()
    {
        var doc = MakeDoc(RepeatText("compression speed non negative", 80));
        Assert.True(doc.GetCompressionSpeed() >= 0);
    }

    [Fact]
    public void GetCompressionSpeed_Consistent()
    {
        var doc = MakeDoc(RepeatText("compression speed consistent", 80));
        Assert.Equal(doc.GetCompressionSpeed(), doc.GetCompressionSpeed());
    }

    [Fact]
    public void GetCompressionSpeed_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("compression speed save load", 80));
        var before = doc.GetCompressionSpeed();
        var path = TempFile("cs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionSpeed(), 2);
    }

    [Fact]
    public void GetCompressionSpeed_Finite()
    {
        var doc = MakeDoc(RepeatText("compression speed finite", 80));
        Assert.True(double.IsFinite(doc.GetCompressionSpeed()));
    }

    // -------------------------------------------------------------------------
    // GetDecompressionSpeed
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressionSpeed_NoThrow()
    {
        var doc = MakeDoc(RepeatText("decompression speed no throw", 80));
        var ex = Record.Exception(() => doc.GetDecompressionSpeed());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDecompressionSpeed_NonNegative()
    {
        var doc = MakeDoc(RepeatText("decompression speed non negative", 80));
        Assert.True(doc.GetDecompressionSpeed() >= 0);
    }

    [Fact]
    public void GetDecompressionSpeed_Consistent()
    {
        var doc = MakeDoc(RepeatText("decompression speed consistent", 80));
        Assert.Equal(doc.GetDecompressionSpeed(), doc.GetDecompressionSpeed());
    }

    [Fact]
    public void GetDecompressionSpeed_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("decompression speed save load", 80));
        var before = doc.GetDecompressionSpeed();
        var path = TempFile("ds_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDecompressionSpeed(), 2);
    }

    [Fact]
    public void GetDecompressionSpeed_Finite()
    {
        var doc = MakeDoc(RepeatText("decompression speed finite", 80));
        Assert.True(double.IsFinite(doc.GetDecompressionSpeed()));
    }

    // -------------------------------------------------------------------------
    // GetMemoryUsage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMemoryUsage_NoThrow()
    {
        var doc = MakeDoc(RepeatText("memory usage no throw", 80));
        var ex = Record.Exception(() => doc.GetMemoryUsage());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMemoryUsage_Positive()
    {
        var doc = MakeDoc(RepeatText("memory usage positive", 80));
        Assert.True(doc.GetMemoryUsage() > 0);
    }

    [Fact]
    public void GetMemoryUsage_Consistent()
    {
        var doc = MakeDoc(RepeatText("memory usage consistent", 80));
        Assert.Equal(doc.GetMemoryUsage(), doc.GetMemoryUsage());
    }

    [Fact]
    public void GetMemoryUsage_SaveLoad_Consistent()
    {
        var doc = MakeDoc(RepeatText("memory usage save load", 80));
        var before = doc.GetMemoryUsage();
        var path = TempFile("mu_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMemoryUsage());
    }

    [Fact]
    public void GetMemoryUsage_AtLeast_DecompressedSize()
    {
        var doc = MakeDoc(RepeatText("memory usage at least decompressed", 80));
        // Memory usage should be >= decompressed size (needs to hold content)
        Assert.True(doc.GetMemoryUsage() >= doc.GetDecompressedSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressionSpeed_GetDecompressionSpeed_GetMemoryUsage_SaveToFile_Pipeline()
    {
        var original = RepeatText("Dogfood speed memory usage content for test", 200);

        var rawPath = TempFile("dogfood_raw.txt");
        File.WriteAllText(rawPath, original);

        var zstPath = TempFile("dogfood_source.zst");
        ZstWriter.CompressFile(rawPath, zstPath, compressionLevel: 3);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.NotNull(doc);
        Assert.True(doc.IsValid);

        // GetCompressionSpeed
        var compSpeed = doc.GetCompressionSpeed();
        Assert.True(compSpeed >= 0);
        Assert.True(double.IsFinite(compSpeed));
        Assert.Equal(compSpeed, doc.GetCompressionSpeed()); // consistent

        // GetDecompressionSpeed
        var decompSpeed = doc.GetDecompressionSpeed();
        Assert.True(decompSpeed >= 0);
        Assert.True(double.IsFinite(decompSpeed));
        Assert.Equal(decompSpeed, doc.GetDecompressionSpeed()); // consistent

        // GetMemoryUsage
        var memUsage = doc.GetMemoryUsage();
        Assert.True(memUsage > 0);
        Assert.Equal(memUsage, doc.GetMemoryUsage()); // consistent
        Assert.True(memUsage >= doc.GetDecompressedSize());

        // Cross-check
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);
        Assert.True(doc.GetCompressionRatio() > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_saved.zst");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(savePath);
        Assert.True(loaded.IsValid);
        Assert.Equal(compSpeed, loaded.GetCompressionSpeed(), 2);
        Assert.Equal(decompSpeed, loaded.GetDecompressionSpeed(), 2);
        Assert.Equal(memUsage, loaded.GetMemoryUsage());

        // Decompress and verify
        var decompPath = TempFile("dogfood_decomp.txt");
        ZstParser.DecompressFile(savePath, decompPath);
        Assert.Equal(original, File.ReadAllText(decompPath));

        // Second doc — level 1 (fastest)
        var raw2 = TempFile("dogfood_raw2.txt");
        File.WriteAllText(raw2, RepeatText("Level 1 fast compression test", 100));
        var zst2 = TempFile("dogfood_src2.zst");
        ZstWriter.CompressFile(raw2, zst2, compressionLevel: 1);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.True(doc2.IsValid);
        Assert.True(doc2.GetCompressionSpeed() >= 0);
        Assert.True(doc2.GetDecompressionSpeed() >= 0);
        Assert.True(doc2.GetMemoryUsage() > 0);

        // Final save
        var finalPath = TempFile("dogfood_final.zst");
        doc2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = ZstDocument.LoadFile(finalPath);
        Assert.True(final.IsValid);
        Assert.Equal(doc2.GetCompressionSpeed(), final.GetCompressionSpeed(), 2);
        Assert.Equal(doc2.GetDecompressionSpeed(), final.GetDecompressionSpeed(), 2);
        Assert.Equal(doc2.GetMemoryUsage(), final.GetMemoryUsage());
    }
}
