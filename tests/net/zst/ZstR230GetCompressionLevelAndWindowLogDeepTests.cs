// Tests for ZstDocument.GetCompressionLevel, GetWindowLog, GetMagicNumber deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R230

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R230: Tests for ZstDocument.GetCompressionLevel, GetWindowLog, GetMagicNumber deeper.
/// GetCompressionLevel(): returns the compression level used (1–22, or 0 if unknown).
/// GetWindowLog(): returns the window log size used during compression.
/// GetMagicNumber(): returns the Zstandard magic number (0xFD2FB528).
/// Covers: GetCompressionLevel no-throw; GetCompressionLevel in range; GetCompressionLevel consistent;
/// GetCompressionLevel save-load;
/// GetWindowLog no-throw; GetWindowLog positive; GetWindowLog consistent; GetWindowLog save-load;
/// GetMagicNumber no-throw; GetMagicNumber equals expected; GetMagicNumber consistent;
/// GetMagicNumber save-load;
/// dogfood Compress→GetCompressionLevel→GetWindowLog→GetMagicNumber→SaveToFile pipeline.
/// </summary>
public class ZstR230GetCompressionLevelAndWindowLogDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR230GetCompressionLevelAndWindowLogDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR230_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateLevel1Zst()
    {
        var content = string.Join("\n", System.Linq.Enumerable.Range(1, 300).Select(i =>
            $"record_{i:D5},value_{i % 100:D3},category_{i % 10},metric_{i * 1.5:F2}"));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content), level: 1);
        var path = TempFile("level1.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateLevel9Zst()
    {
        var content = string.Join("\n", System.Linq.Enumerable.Range(1, 300).Select(i =>
            $"record_{i:D5},value_{i % 100:D3},category_{i % 10},metric_{i * 1.5:F2}"));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content), level: 9);
        var path = TempFile("level9.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    private string CreateStandardZst()
    {
        var content = "Standard Zstandard frame content for magic number and window log tests.\n" +
                      string.Join("\n", System.Linq.Enumerable.Range(1, 100).Select(i => $"line_{i}"));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("standard.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionLevel_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetCompressionLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionLevel_InRange()
    {
        var doc = ZstDocument.LoadFile(CreateLevel9Zst());
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0);
        Assert.True(level <= 22);
    }

    [Fact]
    public void GetCompressionLevel_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetCompressionLevel(), doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLevel9Zst());
        var before = doc.GetCompressionLevel();
        var path = TempFile("cl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionLevel());
    }

    // -------------------------------------------------------------------------
    // GetWindowLog
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowLog_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetWindowLog());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowLog_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetWindowLog() > 0);
    }

    [Fact]
    public void GetWindowLog_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetWindowLog(), doc.GetWindowLog());
    }

    [Fact]
    public void GetWindowLog_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetWindowLog();
        var path = TempFile("wl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowLog());
    }

    // -------------------------------------------------------------------------
    // GetMagicNumber
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetMagicNumber());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicNumber_EqualsExpected()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(0xFD2FB528u, doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetMagicNumber(), doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetMagicNumber();
        var path = TempFile("mn_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMagicNumber());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCompressionLevel_GetWindowLog_GetMagicNumber_SaveToFile_Pipeline()
    {
        // Particle physics event log: simulated LHC collision data
        var sb = new StringBuilder();
        sb.AppendLine("event_id,run_number,luminosity_block,collision_type,energy_tev,particles_detected,vertex_x,vertex_y,vertex_z,missing_et");
        var rng = new Random(137);
        string[] collisions = { "pp", "PbPb", "pPb" };
        for (int i = 0; i < 400; i++)
        {
            double energy = 6.5 + rng.NextDouble() * 7.0;
            int particles = 50 + rng.Next(200);
            double vx = (rng.NextDouble() - 0.5) * 0.1;
            double vy = (rng.NextDouble() - 0.5) * 0.1;
            double vz = (rng.NextDouble() - 0.5) * 100.0;
            double met = rng.NextDouble() * 50.0;
            sb.AppendLine($"EVT_{i:D6},{rng.Next(100000)},{rng.Next(2000)},{collisions[i % 3]},{energy:F4},{particles},{vx:F6},{vy:F6},{vz:F4},{met:F2}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_lhc.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetCompressionLevel
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0);
        Assert.True(level <= 22);
        Assert.Equal(level, doc.GetCompressionLevel()); // consistent

        // GetWindowLog
        var windowLog = doc.GetWindowLog();
        Assert.True(windowLog > 0);
        Assert.Equal(windowLog, doc.GetWindowLog()); // consistent

        // GetMagicNumber
        var magic = doc.GetMagicNumber();
        Assert.Equal(0xFD2FB528u, magic);
        Assert.Equal(magic, doc.GetMagicNumber()); // consistent

        // All frames share the same magic number
        var l1doc = ZstDocument.LoadFile(CreateLevel1Zst());
        Assert.Equal(0xFD2FB528u, l1doc.GetMagicNumber());

        var l9doc = ZstDocument.LoadFile(CreateLevel9Zst());
        Assert.Equal(0xFD2FB528u, l9doc.GetMagicNumber());

        // Level 1 vs level 9 — both have valid compression levels
        Assert.True(l1doc.GetCompressionLevel() >= 0);
        Assert.True(l9doc.GetCompressionLevel() >= 0);

        // Window log consistent across re-reads
        Assert.Equal(l1doc.GetWindowLog(), l1doc.GetWindowLog());

        // SaveToFile
        var out1 = TempFile("dogfood_lhc_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(level, loaded.GetCompressionLevel());
        Assert.Equal(windowLog, loaded.GetWindowLog());
        Assert.Equal(0xFD2FB528u, loaded.GetMagicNumber());

        // Verify decompression works
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        Assert.True(decompressed.Length > 0);

        // Final save
        var out2 = TempFile("dogfood_lhc_v2.zst");
        var recompressed = ZstWriter.Compress(decompressed, level: 3);
        File.WriteAllBytes(out2, recompressed);
        Assert.True(File.Exists(out2));
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetCompressionLevel() >= 0);
        Assert.True(loaded2.GetWindowLog() > 0);
        Assert.Equal(0xFD2FB528u, loaded2.GetMagicNumber());
    }
}
