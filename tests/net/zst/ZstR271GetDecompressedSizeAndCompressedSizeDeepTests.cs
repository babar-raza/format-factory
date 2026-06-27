// Tests for ZstDocument.GetDecompressedSize, GetCompressedSize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R271

using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R271: Tests for ZstDocument.GetDecompressedSize, GetCompressedSize deeper.
/// GetDecompressedSize(): returns the total decompressed byte size of all frames.
/// GetCompressedSize(): returns the total compressed byte size on disk.
/// Covers: GetDecompressedSize no-throw; GetDecompressedSize positive;
/// GetDecompressedSize consistent; GetDecompressedSize save-load;
/// GetCompressedSize no-throw; GetCompressedSize positive;
/// GetCompressedSize leq GetDecompressedSize for compressible data;
/// GetCompressedSize consistent; GetCompressedSize save-load;
/// dogfood pipeline.
/// </summary>
public class ZstR271GetDecompressedSizeAndCompressedSizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR271GetDecompressedSizeAndCompressedSizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR271_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCompressibleZst(string name, int repeatCount = 1000)
    {
        var path = TempFile(name);
        // Highly compressible: repeated ASCII text
        var original = Encoding.UTF8.GetBytes(new string('A', repeatCount) + "end");
        using var ms = new MemoryStream();
        using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
            zs.Write(original, 0, original.Length);
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    private string CreateLargerZst(string name, int size = 10000)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        for (int i = 0; i < size / 50; i++)
            sb.Append($"record_{i:D6}_value_{i * 3 % 97}_pad_xxxx ");
        var original = Encoding.UTF8.GetBytes(sb.ToString());
        using var ms = new MemoryStream();
        using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
            zs.Write(original, 0, original.Length);
        File.WriteAllBytes(path, ms.ToArray());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDecompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressedSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var ex = Record.Exception(() => doc.GetDecompressedSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDecompressedSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        Assert.True(doc.GetDecompressedSize() > 0);
    }

    [Fact]
    public void GetDecompressedSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        Assert.Equal(doc.GetDecompressedSize(), doc.GetDecompressedSize());
    }

    [Fact]
    public void GetDecompressedSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var before = doc.GetDecompressedSize();
        var path = TempFile("dec_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetDecompressedSize());
    }

    // -------------------------------------------------------------------------
    // GetCompressedSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCompressedSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var ex = Record.Exception(() => doc.GetCompressedSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCompressedSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        Assert.True(doc.GetCompressedSize() > 0);
    }

    [Fact]
    public void GetCompressedSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        Assert.Equal(doc.GetCompressedSize(), doc.GetCompressedSize());
    }

    [Fact]
    public void GetCompressedSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateCompressibleZst("sample.zst"));
        var before = doc.GetCompressedSize();
        var path = TempFile("cmp_save.zst");
        doc.SaveToFile(path);
        Assert.Equal(before, ZstDocument.LoadFile(path).GetCompressedSize());
    }

    [Fact]
    public void GetCompressedSize_Leq_DecompressedSize_ForCompressibleData()
    {
        var doc = ZstDocument.LoadFile(CreateLargerZst("large.zst", 10000));
        Assert.True(doc.GetCompressedSize() <= doc.GetDecompressedSize());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDecompressedSize_GetCompressedSize_Pipeline()
    {
        // Scientific — UK Met Office / Copernicus: CAMS Atmospheric Reanalysis
        // Compressed meteorological field data (temperature, pressure, humidity)
        // Decompressed/compressed size ratio quantifies data reduction effectiveness

        var path = TempFile("metoffice_cams_reanalysis.zst");
        {
            // Simulate structured met data: lat/lon grid readings
            var sb = new StringBuilder();
            sb.AppendLine("lat,lon,level_hpa,temp_k,pressure_pa,humidity_pct,wind_u_ms,wind_v_ms,geopotential_m");
            var rng = new Random(20240901);
            // 50.5N to 60.5N, -5W to 5E (UK bounding box), 10 pressure levels
            double[] lats = { 50.5, 52.0, 53.5, 55.0, 56.5, 58.0, 59.5 };
            double[] lons = { -4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5 };
            int[] levels = { 1000, 925, 850, 700, 500, 400, 300, 250, 200, 100 };
            foreach (var lat in lats)
                foreach (var lon in lons)
                    foreach (var lvl in levels)
                    {
                        double temp = 273.15 + 15 * Math.Cos((lat - 55) * Math.PI / 30) - lvl / 50.0 + rng.NextDouble() * 5;
                        double pres = lvl * 100.0 * (1 + 0.001 * rng.NextDouble());
                        double hum = Math.Max(0, Math.Min(100, 60 + 30 * Math.Sin(lon * 0.5) + rng.NextDouble() * 20));
                        double wu = -5 + rng.NextDouble() * 25;
                        double wv = -10 + rng.NextDouble() * 20;
                        double geo = lvl < 500 ? 5000 + (500 - lvl) * 8 : (1000 - lvl) * 25;
                        sb.AppendLine($"{lat:F1},{lon:F1},{lvl},{temp:F2},{pres:F1},{hum:F1},{wu:F2},{wv:F2},{geo:F1}");
                    }
            var original = Encoding.UTF8.GetBytes(sb.ToString());
            using var ms = new MemoryStream();
            using (var zs = new ZLibStream(ms, CompressionLevel.Optimal, leaveOpen: true))
                zs.Write(original, 0, original.Length);
            File.WriteAllBytes(path, ms.ToArray());
        }

        var doc = ZstDocument.LoadFile(path);

        // Decompressed size
        var decSize = doc.GetDecompressedSize();
        Assert.True(decSize > 0);
        Assert.Equal(decSize, doc.GetDecompressedSize()); // consistent

        // Compressed size
        var cmpSize = doc.GetCompressedSize();
        Assert.True(cmpSize > 0);
        Assert.Equal(cmpSize, doc.GetCompressedSize()); // consistent

        // Structured text compresses well
        Assert.True(cmpSize <= decSize);

        // Compression ratio > 1
        double ratio = (double)decSize / cmpSize;
        Assert.True(ratio > 1.0);

        // Frame and magic checks
        Assert.True(doc.GetFrameCount() >= 1);
        Assert.False(string.IsNullOrEmpty(doc.GetMagicBytes()));

        // SaveToFile
        var outPath = TempFile("metoffice_cams_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(decSize, loaded.GetDecompressedSize());
        Assert.Equal(cmpSize, loaded.GetCompressedSize());

        // Second archive: random binary (less compressible)
        var randomPath = TempFile("random_noise.zst");
        {
            var rng2 = new Random(12345);
            var data = new byte[4096];
            rng2.NextBytes(data);
            using var ms2 = new MemoryStream();
            using (var zs2 = new ZLibStream(ms2, CompressionLevel.Fastest, leaveOpen: true))
                zs2.Write(data, 0, data.Length);
            File.WriteAllBytes(randomPath, ms2.ToArray());
        }
        var randDoc = ZstDocument.LoadFile(randomPath);
        Assert.True(randDoc.GetDecompressedSize() > 0);
        Assert.True(randDoc.GetCompressedSize() > 0);

        var ex1 = Record.Exception(() => loaded.GetDecompressedSize());
        var ex2 = Record.Exception(() => loaded.GetCompressedSize());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
