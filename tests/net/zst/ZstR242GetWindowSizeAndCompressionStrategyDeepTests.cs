// Tests for ZstDocument.GetWindowSize, GetCompressionStrategy, GetCompressionLevel deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R242

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R242: Tests for ZstDocument.GetWindowSize, GetCompressionStrategy, GetCompressionLevel deeper.
/// GetWindowSize(): returns the window size used during Zstandard compression (bytes).
/// GetCompressionStrategy(): returns the compression strategy name used (e.g. "fast", "default").
/// GetCompressionLevel(): returns the compression level used (1-22 or 0 for default).
/// Covers: GetWindowSize no-throw; GetWindowSize positive; GetWindowSize consistent;
/// GetWindowSize save-load;
/// GetCompressionStrategy no-throw; GetCompressionStrategy non-null; GetCompressionStrategy consistent;
/// GetCompressionLevel no-throw; GetCompressionLevel non-negative; GetCompressionLevel consistent;
/// GetCompressionLevel save-load;
/// dogfood Compress→GetWindowSize→GetCompressionStrategy→GetCompressionLevel→SaveToFile pipeline.
/// </summary>
public class ZstR242GetWindowSizeAndCompressionStrategyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR242GetWindowSizeAndCompressionStrategyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR242_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStrategyZst()
    {
        var content = string.Join("\n", System.Linq.Enumerable.Repeat(
            "WINDOW_STRATEGY_LEVEL_TEST_ALPHA_BETA_GAMMA_DELTA_EPSILON_ZETA_ETA_THETA_IOTA_KAPPA", 100));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("strategy.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetWindowSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWindowSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        var ex = Record.Exception(() => doc.GetWindowSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWindowSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        Assert.True(doc.GetWindowSize() > 0);
    }

    [Fact]
    public void GetWindowSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        Assert.Equal(doc.GetWindowSize(), doc.GetWindowSize());
    }

    [Fact]
    public void GetWindowSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        var before = doc.GetWindowSize();
        var path = TempFile("ws_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWindowSize());
    }

    // -------------------------------------------------------------------------
    // GetCompressionStrategy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionStrategy_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        var ex = Record.Exception(() => doc.GetCompressionStrategy());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionStrategy_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        Assert.NotNull(doc.GetCompressionStrategy());
    }

    [Fact]
    public void GetCompressionStrategy_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        Assert.Equal(doc.GetCompressionStrategy(), doc.GetCompressionStrategy());
    }

    // -------------------------------------------------------------------------
    // GetCompressionLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressionLevel_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        var ex = Record.Exception(() => doc.GetCompressionLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressionLevel_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        Assert.True(doc.GetCompressionLevel() >= 0);
    }

    [Fact]
    public void GetCompressionLevel_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        Assert.Equal(doc.GetCompressionLevel(), doc.GetCompressionLevel());
    }

    [Fact]
    public void GetCompressionLevel_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateStrategyZst());
        var before = doc.GetCompressionLevel();
        var path = TempFile("cl_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCompressionLevel());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetWindowSize_GetCompressionStrategy_GetCompressionLevel_SaveToFile_Pipeline()
    {
        // Satellite earth observation — multispectral image tile compression metadata inspection
        var sb = new StringBuilder();
        sb.AppendLine("tile_id,acquisition_date,satellite,band,resolution_m,cloud_cover_pct,ndvi,ndwi,urban_index,pixel_count");
        string[] sats = { "Sentinel-2A", "Sentinel-2B", "Landsat-8", "Landsat-9" };
        string[] bands = { "B02_Blue", "B03_Green", "B04_Red", "B08_NIR", "B11_SWIR1", "B12_SWIR2" };
        var rng = new Random(20240901);
        for (int i = 0; i < 400; i++)
        {
            var sat = sats[i % 4];
            var band = bands[i % 6];
            int res = (sat.StartsWith("Sentinel")) ? 10 : 30;
            double cloud = rng.NextDouble() * 30.0;
            double ndvi = -0.2 + rng.NextDouble() * 1.0;
            double ndwi = -0.4 + rng.NextDouble() * 0.8;
            double urban = rng.NextDouble() * 0.6;
            int pixels = 10000 + rng.Next(0, 5000);
            sb.AppendLine($"TILE_{i:D4},2024-{(i % 12 + 1):D2}-{(i % 28 + 1):D2},{sat},{band},{res},{cloud:F1},{ndvi:F3},{ndwi:F3},{urban:F3},{pixels}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_eo_tiles.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetWindowSize
        var windowSize = doc.GetWindowSize();
        Assert.True(windowSize > 0);
        Assert.Equal(windowSize, doc.GetWindowSize()); // consistent

        // GetCompressionStrategy
        var strategy = doc.GetCompressionStrategy();
        Assert.NotNull(strategy);
        Assert.Equal(strategy, doc.GetCompressionStrategy()); // consistent

        // GetCompressionLevel
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0);
        Assert.Equal(level, doc.GetCompressionLevel()); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_eo_tiles_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));

        // LoadFile — verify compression parameters preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(windowSize, loaded.GetWindowSize());
        Assert.NotNull(loaded.GetCompressionStrategy());
        Assert.Equal(level, loaded.GetCompressionLevel());

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("Sentinel-2A", text);
        Assert.Contains("Landsat-8", text);
        Assert.Contains("B04_Red", text);

        // ValidateChecksum
        Assert.True(doc.ValidateChecksum());

        // GetFrameMetadata
        var meta = doc.GetFrameMetadata();
        Assert.NotNull(meta);

        // Second compression and verify
        var recompressed = ZstWriter.Compress(decompressed);
        var out2 = TempFile("dogfood_eo_tiles_v2.zst");
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetWindowSize() > 0);
        Assert.NotNull(loaded2.GetCompressionStrategy());
        Assert.True(loaded2.GetCompressionLevel() >= 0);
        Assert.Equal(0xFD2FB528u, (uint)loaded2.GetMagicNumber());
    }
}
