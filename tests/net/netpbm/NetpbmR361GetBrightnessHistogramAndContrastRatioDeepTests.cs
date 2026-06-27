// Tests for NetpbmImage.GetBrightnessHistogram, GetContrastRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R361

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R361: Tests for NetpbmImage.GetBrightnessHistogram, GetContrastRatio deeper.
/// GetBrightnessHistogram(): returns array of pixel counts per intensity bucket (e.g. 256 buckets).
/// GetContrastRatio(): returns (max-min) / maxIntensity as a measure of dynamic range ∈ [0,1].
/// Covers: GetBrightnessHistogram no-throw; GetBrightnessHistogram non-null;
/// GetBrightnessHistogram sum-equals-pixelCount; GetBrightnessHistogram non-empty;
/// GetBrightnessHistogram save-load; GetContrastRatio no-throw;
/// GetContrastRatio in-range; GetContrastRatio zero for uniform;
/// GetContrastRatio one for full-range; GetContrastRatio consistent;
/// GetContrastRatio save-load;
/// dogfood CreateImage→GetBrightnessHistogram→GetContrastRatio pipeline.
/// </summary>
public class NetpbmR361GetBrightnessHistogramAndContrastRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR361GetBrightnessHistogramAndContrastRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR361_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(int width, int height, int value)
    {
        var path = TempFile($"uniform_{value}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
                sw.Write(c < width - 1 ? $"{value} " : $"{value}");
            sw.WriteLine();
        }
        return path;
    }

    private string CreateFullRangePgm(int width, int height)
    {
        var path = TempFile("fullrange.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                int v = (r * width + c) % 256;
                sw.Write(c < width - 1 ? $"{v} " : $"{v}");
            }
            sw.WriteLine();
        }
        return path;
    }

    private string CreateGradientPgm(int width, int height)
    {
        var path = TempFile("gradient.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                int v = (c * 255) / (width - 1);
                sw.Write(c < width - 1 ? $"{v} " : $"{v}");
            }
            sw.WriteLine();
        }
        return path;
    }

    // -------------------------------------------------------------------------
    // GetBrightnessHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessHistogram_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(50, 50));
        var ex = Record.Exception(() => img.GetBrightnessHistogram());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightnessHistogram_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(50, 50));
        Assert.NotNull(img.GetBrightnessHistogram());
    }

    [Fact]
    public void GetBrightnessHistogram_NonEmpty()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(50, 50));
        Assert.True(img.GetBrightnessHistogram().Length > 0);
    }

    [Fact]
    public void GetBrightnessHistogram_Sum_Equals_PixelCount()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(40, 40));
        var hist = img.GetBrightnessHistogram();
        long total = 0;
        foreach (var v in hist) total += v;
        Assert.Equal((long)(40 * 40), total);
    }

    [Fact]
    public void GetBrightnessHistogram_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(40, 40));
        var before = img.GetBrightnessHistogram();
        var path = TempFile("bh_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        var after = loaded.GetBrightnessHistogram();
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i]);
    }

    // -------------------------------------------------------------------------
    // GetContrastRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(50, 50));
        var ex = Record.Exception(() => img.GetContrastRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrastRatio_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(50, 50));
        var cr = img.GetContrastRatio();
        Assert.True(cr >= 0.0 && cr <= 1.0);
    }

    [Fact]
    public void GetContrastRatio_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(30, 30, 128));
        Assert.Equal(0.0, img.GetContrastRatio(), precision: 6);
    }

    [Fact]
    public void GetContrastRatio_One_ForFullRange()
    {
        var img = NetpbmImage.LoadFile(CreateFullRangePgm(50, 50));
        // Full range 0-255: contrast ratio = (255-0)/255 = 1.0
        Assert.Equal(1.0, img.GetContrastRatio(), precision: 6);
    }

    [Fact]
    public void GetContrastRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(50, 50));
        Assert.Equal(img.GetContrastRatio(), img.GetContrastRatio());
    }

    [Fact]
    public void GetContrastRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(50, 50));
        var before = img.GetContrastRatio();
        var path = TempFile("cr_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetContrastRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBrightnessHistogram_GetContrastRatio_Pipeline()
    {
        // Astronomy — Hubble Space Telescope ACS/WFC image processing
        // Simulated galaxy field: histogram analysis for dynamic range evaluation
        // before and after contrast stretching

        // Create "raw" image: galaxy field — dark background (low values), bright sources (high)
        var rawPath = TempFile("hst_galaxy_raw.pgm");
        using (var sw = new StreamWriter(rawPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("100 100");
            sw.WriteLine("65535"); // 16-bit range
            var rng = new Random(20241201);
            for (int r = 0; r < 100; r++)
            {
                for (int c = 0; c < 100; c++)
                {
                    double distFromCentre = Math.Sqrt((r - 50.0) * (r - 50.0) + (c - 50.0) * (c - 50.0));
                    int v;
                    if (distFromCentre < 8)
                        v = 45000 + rng.Next(5000);       // bright galaxy core
                    else if (distFromCentre < 15)
                        v = 20000 + rng.Next(10000);      // galaxy disk
                    else if (distFromCentre < 22)
                        v = 5000 + rng.Next(5000);        // outer halo
                    else
                        v = 200 + rng.Next(500);           // sky background
                    // Scatter a few point sources
                    if ((r == 20 && c == 25) || (r == 75 && c == 60) || (r == 35 && c == 80))
                        v = 55000 + rng.Next(5000);
                    sw.Write(c < 99 ? $"{v} " : $"{v}");
                }
                sw.WriteLine();
            }
        }

        // Create "contrast-stretched" image: narrow range (8-bit, 200-4000 mapped to 0-255)
        var stretchedPath = TempFile("hst_galaxy_stretched.pgm");
        using (var sw = new StreamWriter(stretchedPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("100 100");
            sw.WriteLine("255");
            var rng = new Random(20241201);
            for (int r = 0; r < 100; r++)
            {
                for (int c = 0; c < 100; c++)
                {
                    // Gradient image: 0-255 across columns (represents stretched output)
                    int v = (c * 255) / 99;
                    sw.Write(c < 99 ? $"{v} " : $"{v}");
                }
                sw.WriteLine();
            }
        }

        Assert.True(File.Exists(rawPath));
        Assert.True(File.Exists(stretchedPath));

        var raw = NetpbmImage.LoadFile(rawPath);
        var stretched = NetpbmImage.LoadFile(stretchedPath);

        // GetBrightnessHistogram — raw image
        var rawHist = raw.GetBrightnessHistogram();
        Assert.NotNull(rawHist);
        Assert.True(rawHist.Length > 0);

        // Sum of histogram = total pixel count
        long rawTotal = 0;
        foreach (var v in rawHist) rawTotal += v;
        Assert.Equal((long)(100 * 100), rawTotal);

        // GetBrightnessHistogram — stretched image
        var stretchedHist = stretched.GetBrightnessHistogram();
        Assert.NotNull(stretchedHist);
        long stretchedTotal = 0;
        foreach (var v in stretchedHist) stretchedTotal += v;
        Assert.Equal((long)(100 * 100), stretchedTotal);

        // GetContrastRatio — raw galaxy field
        var contrastRaw = raw.GetContrastRatio();
        Assert.True(contrastRaw >= 0.0 && contrastRaw <= 1.0);
        Assert.Equal(contrastRaw, raw.GetContrastRatio()); // consistent

        // GetContrastRatio — stretched image (full range 0-255)
        var contrastStretched = stretched.GetContrastRatio();
        Assert.True(contrastStretched >= 0.0 && contrastStretched <= 1.0);
        Assert.Equal(1.0, contrastStretched, precision: 6); // full range gradient = 1.0

        // Basic properties
        Assert.Equal(100, raw.Width);
        Assert.Equal(100, raw.Height);

        // Uniform sky patch: zero contrast
        var skyPath = TempFile("hst_sky_patch.pgm");
        using (var sw = new StreamWriter(skyPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("40 40");
            sw.WriteLine("65535");
            for (int r = 0; r < 40; r++)
            {
                for (int c = 0; c < 40; c++)
                    sw.Write(c < 39 ? "300 " : "300");
                sw.WriteLine();
            }
        }
        var sky = NetpbmImage.LoadFile(skyPath);
        Assert.Equal(0.0, sky.GetContrastRatio(), precision: 6);

        var skyHist = sky.GetBrightnessHistogram();
        long skyTotal = 0;
        foreach (var v in skyHist) skyTotal += v;
        Assert.Equal((long)(40 * 40), skyTotal);

        // SaveToFile and verify
        var outPath = TempFile("hst_stretched_out.pgm");
        stretched.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        var loadedStretched = NetpbmImage.LoadFile(outPath);
        Assert.Equal(contrastStretched, loadedStretched.GetContrastRatio(), precision: 6);

        var loadedHist = loadedStretched.GetBrightnessHistogram();
        Assert.Equal(stretchedHist.Length, loadedHist.Length);
        long loadedTotal = 0;
        foreach (var v in loadedHist) loadedTotal += v;
        Assert.Equal((long)(100 * 100), loadedTotal);

        // No-throw checks
        var ex1 = Record.Exception(() => loadedStretched.GetBrightnessHistogram());
        var ex2 = Record.Exception(() => loadedStretched.GetContrastRatio());
        var ex3 = Record.Exception(() => loadedStretched.GetMeanIntensity());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
