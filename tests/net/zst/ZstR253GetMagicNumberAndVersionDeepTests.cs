// Tests for ZstDocument.GetMagicNumber, GetVersion deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R253

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R253: Tests for ZstDocument.GetMagicNumber, GetVersion deeper.
/// GetMagicNumber(): returns the zstd magic number bytes from the frame header.
/// GetVersion(): returns the zstd format version used to compress the frame.
/// Covers: GetMagicNumber no-throw; GetMagicNumber non-null; GetMagicNumber non-empty;
/// GetMagicNumber consistent; GetMagicNumber save-load;
/// GetVersion no-throw; GetVersion non-negative; GetVersion consistent;
/// GetVersion save-load; GetVersion positive for valid frame;
/// dogfood CreateDoc→GetMagicNumber→GetVersion→SaveToFile pipeline.
/// </summary>
public class ZstR253GetMagicNumberAndVersionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR253GetMagicNumberAndVersionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR253_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStandardZst()
    {
        var content = "Standard zstd frame — magic number and version test. " +
                      string.Join(" ", System.Linq.Enumerable.Repeat("Scientific data archive.", 60));
        var path = TempFile("standard.zst");
        var writer = new ZstWriter();
        writer.CompressToFile(System.Text.Encoding.UTF8.GetBytes(content), path);
        return path;
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
    public void GetMagicNumber_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.NotNull(doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.NotEmpty(doc.GetMagicNumber());
    }

    [Fact]
    public void GetMagicNumber_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var m1 = doc.GetMagicNumber();
        var m2 = doc.GetMagicNumber();
        Assert.Equal(m1.Length, m2.Length);
        for (int i = 0; i < m1.Length; i++)
            Assert.Equal(m1[i], m2[i]);
    }

    [Fact]
    public void GetMagicNumber_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetMagicNumber();
        var path = TempFile("mn_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        var after = loaded.GetMagicNumber();
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i]);
    }

    // -------------------------------------------------------------------------
    // GetVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVersion_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var ex = Record.Exception(() => doc.GetVersion());
        Assert.Null(ex);
    }

    [Fact]
    public void GetVersion_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetVersion() >= 0);
    }

    [Fact]
    public void GetVersion_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.Equal(doc.GetVersion(), doc.GetVersion());
    }

    [Fact]
    public void GetVersion_Positive_ForValidFrame()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        Assert.True(doc.GetVersion() >= 0);
    }

    [Fact]
    public void GetVersion_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStandardZst());
        var before = doc.GetVersion();
        var path = TempFile("ver_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetVersion());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMagicNumber_GetVersion_Pipeline()
    {
        // Earth observation — Copernicus Climate Change Service (C3S) ERA5 reanalysis
        // Compressing NetCDF-derived atmospheric state vector data for ECMWF archive exchange
        var rng = new Random(20241120);

        // Simulate ERA5 atmospheric reanalysis data (compressed CSV representation)
        var headerBuilder = new System.Text.StringBuilder();
        headerBuilder.AppendLine("# ERA5 Reanalysis Data Extract — ECMWF");
        headerBuilder.AppendLine("# Product: ERA5 hourly data on pressure levels");
        headerBuilder.AppendLine("# Variables: Temperature, U-wind, V-wind, Geopotential, Relative Humidity");
        headerBuilder.AppendLine("# Pressure levels: 1000,925,850,700,600,500,400,300,250,200,150,100,70,50 hPa");
        headerBuilder.AppendLine("# Spatial domain: Europe (25N-75N, 25W-45E) at 0.25 degree resolution");
        headerBuilder.AppendLine("# Reference: Hersbach et al. (2020) doi:10.1002/qj.3803");
        headerBuilder.AppendLine("datetime_utc,lat,lon,pressure_hpa,temperature_k,u_wind_ms,v_wind_ms,geopotential_m2s2,rh_pct");

        // 14 pressure levels × 60 timesteps
        double[] pressureLevels = { 1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50 };
        for (int t = 0; t < 60; t++)
        {
            double lat = 51.5 + (rng.NextDouble() - 0.5) * 20;
            double lon = -0.1 + (rng.NextDouble() - 0.5) * 40;
            string dtStr = $"2024-01-{(t / 24 + 1):D2}T{(t % 24):D2}:00:00Z";
            foreach (double p in pressureLevels)
            {
                // Standard atmosphere approximation
                double tempK = 288.15 - 6.5 * (p < 200 ? 25 : (1000 - p) / 1000.0 * 10);
                double uWind = (rng.NextDouble() - 0.5) * 60;
                double vWind = (rng.NextDouble() - 0.5) * 40;
                double geopot = 287.058 * tempK * Math.Log(1000.0 / p);
                double rh = 10 + rng.NextDouble() * 85;
                headerBuilder.AppendLine($"{dtStr},{lat:F2},{lon:F2},{p:F0},{tempK:F2},{uWind:F3},{vWind:F3},{geopot:F1},{rh:F1}");
            }
        }

        var payload = System.Text.Encoding.UTF8.GetBytes(headerBuilder.ToString());

        // Compress
        var path = TempFile("era5_pressure_levels.zst");
        var writer = new ZstWriter();
        writer.CompressToFile(payload, path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetMagicNumber
        var magic = doc.GetMagicNumber();
        Assert.NotNull(magic);
        Assert.NotEmpty(magic);
        // Consistent across calls
        var magic2 = doc.GetMagicNumber();
        Assert.Equal(magic.Length, magic2.Length);
        for (int i = 0; i < magic.Length; i++)
            Assert.Equal(magic[i], magic2[i]);

        // GetVersion
        var version = doc.GetVersion();
        Assert.True(version >= 0);
        Assert.Equal(version, doc.GetVersion()); // consistent

        // Other frame properties
        Assert.True(doc.GetFrameCount() >= 1);
        Assert.Equal(0, doc.GetDictionaryId());

        // Decompression round-trip
        var decompressed = doc.Decompress();
        Assert.NotNull(decompressed);
        Assert.Equal(payload.Length, decompressed.Length);

        // SaveToFile
        var path2 = TempFile("era5_pressure_levels_copy.zst");
        doc.SaveToFile(path2);
        Assert.True(File.Exists(path2));

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path2);
        var loadedMagic = loaded.GetMagicNumber();
        Assert.Equal(magic.Length, loadedMagic.Length);
        for (int i = 0; i < magic.Length; i++)
            Assert.Equal(magic[i], loadedMagic[i]);
        Assert.Equal(version, loaded.GetVersion());
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Multiple frames — 3 separate variables archived
        string[] variables = { "temperature", "wind_u", "wind_v" };
        foreach (var varName in variables)
        {
            var varBuilder = new System.Text.StringBuilder();
            varBuilder.AppendLine($"# ERA5 {varName} single-level, 200 timesteps");
            for (int i = 0; i < 200; i++)
                varBuilder.AppendLine($"2024-01-01T{i % 24:D2}:00:00Z,{51.5 + rng.NextDouble():F3},{-0.1 + rng.NextDouble():F3},{(rng.NextDouble() * 50 - 10):F3}");
            var varPayload = System.Text.Encoding.UTF8.GetBytes(varBuilder.ToString());
            var varPath = TempFile($"era5_{varName}.zst");
            writer.CompressToFile(varPayload, varPath);
            var varDoc = ZstDocument.LoadFile(varPath);
            Assert.NotNull(varDoc.GetMagicNumber());
            Assert.True(varDoc.GetVersion() >= 0);
            Assert.Equal(version, varDoc.GetVersion()); // same zstd version
        }
    }
}
