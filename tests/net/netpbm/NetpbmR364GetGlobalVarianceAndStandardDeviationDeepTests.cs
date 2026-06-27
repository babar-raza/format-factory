// Tests for NetpbmImage.GetGlobalVariance, GetGlobalStandardDeviation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R364

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R364: Tests for NetpbmImage.GetGlobalVariance, GetGlobalStandardDeviation deeper.
/// GetGlobalVariance(): returns the variance of all pixel intensity values.
/// GetGlobalStandardDeviation(): returns the standard deviation of all pixel intensities.
/// Covers: GetGlobalVariance no-throw; GetGlobalVariance non-negative; GetGlobalVariance consistent;
/// GetGlobalVariance zero for uniform; GetGlobalVariance save-load;
/// GetGlobalStandardDeviation no-throw; GetGlobalStandardDeviation non-negative;
/// GetGlobalStandardDeviation consistent; GetGlobalStandardDeviation zero for uniform;
/// GetGlobalStandardDeviation equals sqrt(variance); GetGlobalStandardDeviation save-load;
/// dogfood CreateImage→GetGlobalVariance→GetGlobalStandardDeviation pipeline.
/// </summary>
public class NetpbmR364GetGlobalVarianceAndStandardDeviationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR364GetGlobalVarianceAndStandardDeviationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR364_" + Guid.NewGuid().ToString("N"));
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

    private string CreateVariedPgm(int width, int height, int seed)
    {
        var path = TempFile($"varied_{seed}.pgm");
        var rng = new Random(seed);
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                int v = rng.Next(256);
                sw.Write(c < width - 1 ? $"{v} " : $"{v}");
            }
            sw.WriteLine();
        }
        return path;
    }

    private string CreateHighVariancePgm(int width, int height)
    {
        var path = TempFile("highvariance.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                // Alternating 0 and 255 — maximum variance
                int v = (r + c) % 2 == 0 ? 0 : 255;
                sw.Write(c < width - 1 ? $"{v} " : $"{v}");
            }
            sw.WriteLine();
        }
        return path;
    }

    // -------------------------------------------------------------------------
    // GetGlobalVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGlobalVariance_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(50, 50, 42));
        var ex = Record.Exception(() => img.GetGlobalVariance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGlobalVariance_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(50, 50, 42));
        Assert.True(img.GetGlobalVariance() >= 0);
    }

    [Fact]
    public void GetGlobalVariance_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(50, 50, 42));
        Assert.Equal(img.GetGlobalVariance(), img.GetGlobalVariance());
    }

    [Fact]
    public void GetGlobalVariance_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(30, 30, 128));
        Assert.Equal(0.0, img.GetGlobalVariance(), precision: 6);
    }

    [Fact]
    public void GetGlobalVariance_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(40, 40, 42));
        var before = img.GetGlobalVariance();
        var path = TempFile("gv_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetGlobalVariance(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetGlobalStandardDeviation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGlobalStandardDeviation_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(50, 50, 42));
        var ex = Record.Exception(() => img.GetGlobalStandardDeviation());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGlobalStandardDeviation_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(50, 50, 42));
        Assert.True(img.GetGlobalStandardDeviation() >= 0);
    }

    [Fact]
    public void GetGlobalStandardDeviation_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(50, 50, 42));
        Assert.Equal(img.GetGlobalStandardDeviation(), img.GetGlobalStandardDeviation());
    }

    [Fact]
    public void GetGlobalStandardDeviation_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(30, 30, 200));
        Assert.Equal(0.0, img.GetGlobalStandardDeviation(), precision: 6);
    }

    [Fact]
    public void GetGlobalStandardDeviation_Equals_Sqrt_Variance()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(50, 50, 42));
        var variance = img.GetGlobalVariance();
        var std = img.GetGlobalStandardDeviation();
        Assert.Equal(Math.Sqrt(variance), std, precision: 4);
    }

    [Fact]
    public void GetGlobalStandardDeviation_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateVariedPgm(40, 40, 42));
        var before = img.GetGlobalStandardDeviation();
        var path = TempFile("gsd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetGlobalStandardDeviation(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetGlobalVariance_GetGlobalStandardDeviation_Pipeline()
    {
        // Spectroscopy — Diamond Light Source (Harwell) X-ray powder diffraction images
        // Simulated detector images: variance analysis for background correction and peak identification

        // "Blank" detector: low signal, low variance (detector noise floor)
        var blankPath = TempFile("dls_blank_detector.pgm");
        using (var sw = new StreamWriter(blankPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("80 80");
            sw.WriteLine("65535");
            var rng = new Random(20241201);
            for (int r = 0; r < 80; r++)
            {
                for (int c = 0; c < 80; c++)
                {
                    // Low-level noise around 1000 counts
                    int v = 950 + rng.Next(100);
                    sw.Write(c < 79 ? $"{v} " : $"{v}");
                }
                sw.WriteLine();
            }
        }

        // "Sample" detector: diffraction rings — high dynamic range, high variance
        var samplePath = TempFile("dls_sample_diffraction.pgm");
        using (var sw = new StreamWriter(samplePath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("80 80");
            sw.WriteLine("65535");
            var rng = new Random(20241201);
            for (int r = 0; r < 80; r++)
            {
                for (int c = 0; c < 80; c++)
                {
                    // Simulate diffraction rings at specific radii
                    double dist = Math.Sqrt((r - 40.0) * (r - 40.0) + (c - 40.0) * (c - 40.0));
                    int v;
                    if (Math.Abs(dist - 15) < 1.5 || Math.Abs(dist - 25) < 1.5 || Math.Abs(dist - 35) < 1.5)
                        v = 40000 + rng.Next(15000); // Bragg peaks: high intensity
                    else
                        v = 800 + rng.Next(400);     // background: low intensity
                    sw.Write(c < 79 ? $"{v} " : $"{v}");
                }
                sw.WriteLine();
            }
        }

        Assert.True(File.Exists(blankPath));
        Assert.True(File.Exists(samplePath));

        var blank = NetpbmImage.LoadFile(blankPath);
        var sample = NetpbmImage.LoadFile(samplePath);

        // GetGlobalVariance
        var varianceBlank = blank.GetGlobalVariance();
        var varianceSample = sample.GetGlobalVariance();
        Assert.True(varianceBlank >= 0);
        Assert.True(varianceSample >= 0);
        Assert.Equal(varianceBlank, blank.GetGlobalVariance()); // consistent
        Assert.Equal(varianceSample, sample.GetGlobalVariance());

        // Sample with diffraction peaks has higher variance than blank
        Assert.True(varianceSample > varianceBlank);

        // GetGlobalStandardDeviation
        var stdBlank = blank.GetGlobalStandardDeviation();
        var stdSample = sample.GetGlobalStandardDeviation();
        Assert.True(stdBlank >= 0);
        Assert.True(stdSample >= 0);

        // sqrt(variance) = std
        Assert.Equal(Math.Sqrt(varianceBlank), stdBlank, precision: 4);
        Assert.Equal(Math.Sqrt(varianceSample), stdSample, precision: 4);

        // Sample has higher std
        Assert.True(stdSample > stdBlank);

        // Uniform image: zero variance
        var uniformPath = TempFile("dls_uniform.pgm");
        using (var sw = new StreamWriter(uniformPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("40 40");
            sw.WriteLine("65535");
            for (int r = 0; r < 40; r++)
            {
                for (int c = 0; c < 40; c++)
                    sw.Write(c < 39 ? "1000 " : "1000");
                sw.WriteLine();
            }
        }
        var uniform = NetpbmImage.LoadFile(uniformPath);
        Assert.Equal(0.0, uniform.GetGlobalVariance(), precision: 6);
        Assert.Equal(0.0, uniform.GetGlobalStandardDeviation(), precision: 6);

        // Basic properties
        Assert.Equal(80, sample.Width);
        Assert.Equal(80, sample.Height);

        // SaveToFile and verify
        var outPath = TempFile("dls_sample_out.pgm");
        sample.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        var loadedSample = NetpbmImage.LoadFile(outPath);
        Assert.Equal(varianceSample, loadedSample.GetGlobalVariance(), precision: 6);
        Assert.Equal(stdSample, loadedSample.GetGlobalStandardDeviation(), precision: 6);

        var ex1 = Record.Exception(() => loadedSample.GetGlobalVariance());
        var ex2 = Record.Exception(() => loadedSample.GetGlobalStandardDeviation());
        var ex3 = Record.Exception(() => loadedSample.GetMeanIntensity());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
