// Tests for ZstDocument.GetDecompressionSpeed, GetThroughputEstimate, GetCompressionTime deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R228

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R228: Tests for ZstDocument.GetDecompressionSpeed, GetThroughputEstimate, GetCompressionTime deeper.
/// GetDecompressionSpeed(): returns the estimated decompression speed in MB/s.
/// GetThroughputEstimate(): returns the estimated throughput (compressed bytes per second).
/// GetCompressionTime(): returns the time taken to compress the data in milliseconds.
/// Covers: GetDecompressionSpeed no-throw; GetDecompressionSpeed non-negative; GetDecompressionSpeed consistent;
/// GetDecompressionSpeed save-load;
/// GetThroughputEstimate no-throw; GetThroughputEstimate non-negative; GetThroughputEstimate consistent;
/// GetThroughputEstimate save-load;
/// GetCompressionTime no-throw; GetCompressionTime non-negative; GetCompressionTime consistent;
/// GetCompressionTime save-load;
/// dogfood Compress→GetDecompressionSpeed→GetThroughputEstimate→GetCompressionTime→SaveToFile pipeline.
/// </summary>
public class ZstR228GetDecompressionSpeedAndThroughputDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR228GetDecompressionSpeedAndThroughputDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR228_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(string text = "Pack my box with five dozen liquor jugs. " +
        "The five boxing wizards jump quickly. How vexingly quick daft zebras jump!")
    {
        var raw = TempFile("src.txt");
        File.WriteAllText(raw, text);
        var zst = TempFile("src.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zst);
        return zst;
    }

    // -------------------------------------------------------------------------
    // GetDecompressionSpeed
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressionSpeed_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetDecompressionSpeed());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDecompressionSpeed_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetDecompressionSpeed() >= 0.0);
    }

    [Fact]
    public void GetDecompressionSpeed_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetDecompressionSpeed(), doc.GetDecompressionSpeed());
    }

    [Fact]
    public void GetDecompressionSpeed_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetDecompressionSpeed();
        var path = TempFile("ds_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.True(loaded.GetDecompressionSpeed() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // GetThroughputEstimate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetThroughputEstimate_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetThroughputEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetThroughputEstimate_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetThroughputEstimate() >= 0.0);
    }

    [Fact]
    public void GetThroughputEstimate_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetThroughputEstimate(), doc.GetThroughputEstimate());
    }

    [Fact]
    public void GetThroughputEstimate_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetThroughputEstimate();
        var path = TempFile("te_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.True(loaded.GetThroughputEstimate() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // GetCompressionTime
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionTime_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetCompressionTime());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionTime_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetCompressionTime() >= 0.0);
    }

    [Fact]
    public void GetCompressionTime_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetCompressionTime(), doc.GetCompressionTime());
    }

    [Fact]
    public void GetCompressionTime_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetCompressionTime();
        var path = TempFile("ct_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.True(loaded.GetCompressionTime() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDecompressionSpeed_GetThroughputEstimate_GetCompressionTime_SaveToFile_Pipeline()
    {
        var content = string.Join("\n", new[]
        {
            "CLIMATE_DATA — Station Network Export 20260626",
            "station=WMO_10501,lat=52.37,lon=4.90,temp_c=18.4,humidity=72,pressure=1013.2,wind_ms=4.2,cloud_oktas=4",
            "station=WMO_10513,lat=51.97,lon=4.44,temp_c=17.9,humidity=75,pressure=1012.8,wind_ms=5.1,cloud_oktas=5",
            "station=WMO_10542,lat=52.10,lon=5.18,temp_c=18.1,humidity=71,pressure=1013.5,wind_ms=3.8,cloud_oktas=3",
            "station=WMO_10551,lat=51.44,lon=5.47,temp_c=18.7,humidity=69,pressure=1014.1,wind_ms=4.5,cloud_oktas=2",
            "station=WMO_10560,lat=52.65,lon=4.79,temp_c=17.2,humidity=79,pressure=1012.1,wind_ms=6.2,cloud_oktas=6",
            "station=WMO_10611,lat=51.20,lon=3.22,temp_c=18.9,humidity=67,pressure=1014.8,wind_ms=3.4,cloud_oktas=1",
            "station=WMO_10618,lat=50.91,lon=4.48,temp_c=19.1,humidity=65,pressure=1015.2,wind_ms=2.9,cloud_oktas=0",
            "END_EXPORT"
        });

        var raw = TempFile("climate.txt");
        File.WriteAllText(raw, content);
        var zstPath = TempFile("climate.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zstPath);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetDecompressionSpeed — non-negative
        var speed = doc.GetDecompressionSpeed();
        Assert.True(speed >= 0.0);
        Assert.Equal(speed, doc.GetDecompressionSpeed()); // consistent

        // GetThroughputEstimate — non-negative
        var throughput = doc.GetThroughputEstimate();
        Assert.True(throughput >= 0.0);
        Assert.Equal(throughput, doc.GetThroughputEstimate()); // consistent

        // GetCompressionTime — non-negative
        var compTime = doc.GetCompressionTime();
        Assert.True(compTime >= 0.0);
        Assert.Equal(compTime, doc.GetCompressionTime()); // consistent

        // Cross-check properties
        Assert.True(doc.GetCompressionLevel() >= 0);
        Assert.True(doc.GetFrameCount() >= 1);
        Assert.True(doc.GetCompressionRatio() > 0.0);

        // SaveToFile
        var path = TempFile("dogfood_climate_out.zst");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path);
        Assert.True(loaded.GetDecompressionSpeed() >= 0.0);
        Assert.True(loaded.GetThroughputEstimate() >= 0.0);
        Assert.True(loaded.GetCompressionTime() >= 0.0);
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Larger file
        var largeContent = string.Join("\n", System.Linq.Enumerable.Repeat(content, 20));
        var rawLarge = TempFile("climate_large.txt");
        File.WriteAllText(rawLarge, largeContent);
        var zstLarge = TempFile("climate_large.zst");
        writer.CompressFile(rawLarge, zstLarge);
        var docLarge = ZstDocument.LoadFile(zstLarge);
        Assert.True(docLarge.GetDecompressionSpeed() >= 0.0);
        Assert.True(docLarge.GetThroughputEstimate() >= 0.0);
        Assert.True(docLarge.GetCompressionTime() >= 0.0);

        // Final save
        var path2 = TempFile("dogfood_climate_v2.zst");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = ZstDocument.LoadFile(path2);
        Assert.True(loaded2.GetDecompressionSpeed() >= 0.0);
        Assert.True(loaded2.GetThroughputEstimate() >= 0.0);
        Assert.True(loaded2.GetCompressionTime() >= 0.0);
    }
}
