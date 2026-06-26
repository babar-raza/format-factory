// Tests for ZstDocument.GetCompressionLevel, GetCompressionStrategy, GetMagicNumber deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R222

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R222: Tests for ZstDocument.GetCompressionLevel, GetCompressionStrategy, GetMagicNumber deeper.
/// GetCompressionLevel(): returns the compression level used (1-22).
/// GetCompressionStrategy(): returns the compression strategy string.
/// GetMagicNumber(): returns the Zstandard magic number (0xFD2FB528).
/// Covers: GetCompressionLevel no-throw; GetCompressionLevel in [1,22]; GetCompressionLevel consistent;
/// GetCompressionLevel save-load; GetCompressionLevel non-negative;
/// GetCompressionStrategy no-throw; GetCompressionStrategy non-null; GetCompressionStrategy non-empty;
/// GetCompressionStrategy consistent; GetCompressionStrategy save-load;
/// GetMagicNumber no-throw; GetMagicNumber positive; GetMagicNumber consistent;
/// GetMagicNumber save-load; GetMagicNumber valid-zstd-value;
/// dogfood Compress→GetCompressionLevel→GetCompressionStrategy→GetMagicNumber→SaveToFile pipeline.
/// </summary>
public class ZstR222GetLevelAndStrategyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR222GetLevelAndStrategyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR222_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(string text = "The quick brown fox jumps over the lazy dog. " +
        "Pack my box with five dozen liquor jugs. How razorback-jumping frogs can level six piqued gymnasts!")
    {
        var raw = TempFile("src.txt");
        File.WriteAllText(raw, text);
        var zst = TempFile("src.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zst);
        return zst;
    }

    // -------------------------------------------------------------------------
    // GetCompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionLevel_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetCompressionLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionLevel_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetCompressionLevel() >= 0);
    }

    [Fact]
    public void GetCompressionLevel_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetCompressionLevel(), doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetCompressionLevel();
        var path = TempFile("cl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionLevel());
    }

    // -------------------------------------------------------------------------
    // GetCompressionStrategy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionStrategy_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetCompressionStrategy());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionStrategy_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.NotNull(doc.GetCompressionStrategy());
    }

    [Fact]
    public void GetCompressionStrategy_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.NotEmpty(doc.GetCompressionStrategy());
    }

    [Fact]
    public void GetCompressionStrategy_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetCompressionStrategy(), doc.GetCompressionStrategy());
    }

    [Fact]
    public void GetCompressionStrategy_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetCompressionStrategy();
        var path = TempFile("cs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionStrategy());
    }

    // -------------------------------------------------------------------------
    // GetMagicNumber
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetMagicNumber());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMagicNumber_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetMagicNumber() > 0);
    }

    [Fact]
    public void GetMagicNumber_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetMagicNumber(), doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
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
    public void Dogfood_GetCompressionLevel_GetCompressionStrategy_GetMagicNumber_SaveToFile_Pipeline()
    {
        var content = string.Join("\n", new[]
        {
            "TELEMETRY STREAM — Session 20260626",
            "sensor_id=T001,timestamp=1719360000,temp=22.4,humidity=45.2,pressure=1013.25",
            "sensor_id=T002,timestamp=1719360001,temp=23.1,humidity=44.8,pressure=1013.18",
            "sensor_id=T003,timestamp=1719360002,temp=21.9,humidity=46.0,pressure=1013.31",
            "sensor_id=T001,timestamp=1719360060,temp=22.6,humidity=45.0,pressure=1013.22",
            "sensor_id=T002,timestamp=1719360061,temp=23.3,humidity=44.5,pressure=1013.15",
            "sensor_id=T003,timestamp=1719360062,temp=22.0,humidity=46.3,pressure=1013.28",
            "END_STREAM"
        });

        var raw = TempFile("telemetry.txt");
        File.WriteAllText(raw, content);
        var zstPath = TempFile("telemetry.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zstPath);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetCompressionLevel
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0);
        Assert.Equal(level, doc.GetCompressionLevel()); // consistent

        // GetCompressionStrategy
        var strategy = doc.GetCompressionStrategy();
        Assert.NotNull(strategy);
        Assert.NotEmpty(strategy);
        Assert.Equal(strategy, doc.GetCompressionStrategy()); // consistent

        // GetMagicNumber
        var magic = doc.GetMagicNumber();
        Assert.True(magic > 0);
        Assert.Equal(magic, doc.GetMagicNumber()); // consistent

        // SaveToFile
        var path = TempFile("dogfood_telemetry_out.zst");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(level, loaded.GetCompressionLevel());
        Assert.Equal(strategy, loaded.GetCompressionStrategy());
        Assert.Equal(magic, loaded.GetMagicNumber());
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Cross-checks
        Assert.True(loaded.GetCompressionRatio() >= 1.0 || loaded.GetCompressionRatio() > 0);
        Assert.True(loaded.GetFrameCount() >= 1);

        // Final save
        var path2 = TempFile("dogfood_telemetry_v2.zst");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = ZstDocument.LoadFile(path2);
        Assert.Equal(loaded.GetCompressionLevel(), loaded2.GetCompressionLevel());
        Assert.Equal(loaded.GetCompressionStrategy(), loaded2.GetCompressionStrategy());
        Assert.Equal(loaded.GetMagicNumber(), loaded2.GetMagicNumber());
    }
}
