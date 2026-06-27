// Tests for NetpbmImage.GetNoiseEstimate, GetSignalToNoiseRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R359

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R359: Tests for NetpbmImage.GetNoiseEstimate, GetSignalToNoiseRatio deeper.
/// GetNoiseEstimate(): returns estimated pixel noise level (standard deviation of local variation).
/// GetSignalToNoiseRatio(): returns ratio of mean signal to noise estimate (higher = cleaner image).
/// Covers: GetNoiseEstimate no-throw; GetNoiseEstimate non-negative; GetNoiseEstimate consistent;
/// GetNoiseEstimate zero for uniform; GetNoiseEstimate save-load;
/// GetSignalToNoiseRatio no-throw; GetSignalToNoiseRatio non-negative;
/// GetSignalToNoiseRatio consistent; GetSignalToNoiseRatio save-load;
/// GetSignalToNoiseRatio higher for smooth vs noisy;
/// dogfood CreateImage→GetNoiseEstimate→GetSignalToNoiseRatio pipeline.
/// </summary>
public class NetpbmR359GetNoiseEstimateAndSignalToNoiseRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR359GetNoiseEstimateAndSignalToNoiseRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR359_" + Guid.NewGuid().ToString("N"));
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

    private string CreateNoisyPgm(int width, int height, int baseValue, int noiseAmp, int seed)
    {
        var path = TempFile("noisy.pgm");
        var rng = new Random(seed);
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                int v = Math.Clamp(baseValue + rng.Next(-noiseAmp, noiseAmp + 1), 0, 255);
                sw.Write(c < width - 1 ? $"{v} " : $"{v}");
            }
            sw.WriteLine();
        }
        return path;
    }

    private string CreateSmoothPgm(int width, int height)
    {
        var path = TempFile("smooth.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int r = 0; r < height; r++)
        {
            // Gentle horizontal gradient: very low noise
            for (int c = 0; c < width; c++)
            {
                int v = 120 + (c * 10 / width);
                sw.Write(c < width - 1 ? $"{v} " : $"{v}");
            }
            sw.WriteLine();
        }
        return path;
    }

    // -------------------------------------------------------------------------
    // GetNoiseEstimate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoiseEstimate_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        var ex = Record.Exception(() => img.GetNoiseEstimate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNoiseEstimate_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        Assert.True(img.GetNoiseEstimate() >= 0);
    }

    [Fact]
    public void GetNoiseEstimate_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        Assert.Equal(img.GetNoiseEstimate(), img.GetNoiseEstimate());
    }

    [Fact]
    public void GetNoiseEstimate_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(30, 30, 128));
        Assert.Equal(0.0, img.GetNoiseEstimate(), precision: 6);
    }

    [Fact]
    public void GetNoiseEstimate_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        var before = img.GetNoiseEstimate();
        var path = TempFile("ne_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetNoiseEstimate(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetSignalToNoiseRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSignalToNoiseRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        var ex = Record.Exception(() => img.GetSignalToNoiseRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSignalToNoiseRatio_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        Assert.True(img.GetSignalToNoiseRatio() >= 0);
    }

    [Fact]
    public void GetSignalToNoiseRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        Assert.Equal(img.GetSignalToNoiseRatio(), img.GetSignalToNoiseRatio());
    }

    [Fact]
    public void GetSignalToNoiseRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 30, 42));
        var before = img.GetSignalToNoiseRatio();
        var path = TempFile("snr_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetSignalToNoiseRatio(), precision: 6);
    }

    [Fact]
    public void GetSignalToNoiseRatio_Higher_ForSmooth_ThanNoisy()
    {
        var smooth = NetpbmImage.LoadFile(CreateSmoothPgm(50, 50));
        var noisy = NetpbmImage.LoadFile(CreateNoisyPgm(50, 50, 128, 40, 99));
        // Smooth image has higher SNR than heavily noisy one
        Assert.True(smooth.GetSignalToNoiseRatio() >= noisy.GetSignalToNoiseRatio());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNoiseEstimate_GetSignalToNoiseRatio_Pipeline()
    {
        // Medical imaging — CT scan image quality assessment
        // Simulated axial CT slices: evaluate noise and SNR for dose optimisation
        // Low-dose CT has higher noise; full-dose CT has lower noise and higher SNR

        // Create "full-dose" CT slice: smooth mid-grey with subtle anatomical gradient
        var fullDosePath = TempFile("ct_full_dose.pgm");
        using (var sw = new StreamWriter(fullDosePath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("80 80");
            sw.WriteLine("4095"); // 12-bit grayscale range
            var rng = new Random(20241115);
            for (int r = 0; r < 80; r++)
            {
                for (int c = 0; c < 80; c++)
                {
                    // Simulate soft tissue (centre) vs bone (ring) vs air (outer)
                    double dist = Math.Sqrt((r - 40.0) * (r - 40.0) + (c - 40.0) * (c - 40.0));
                    int baseVal;
                    if (dist < 15) baseVal = 2000;       // soft tissue
                    else if (dist < 25) baseVal = 3500;   // bone
                    else if (dist < 35) baseVal = 1800;   // mixed
                    else baseVal = 200;                    // air
                    // Low noise (full dose)
                    int v = Math.Clamp(baseVal + rng.Next(-20, 21), 0, 4095);
                    sw.Write(c < 79 ? $"{v} " : $"{v}");
                }
                sw.WriteLine();
            }
        }

        // Create "low-dose" CT slice: same anatomy but high noise
        var lowDosePath = TempFile("ct_low_dose.pgm");
        using (var sw = new StreamWriter(lowDosePath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("80 80");
            sw.WriteLine("4095");
            var rng = new Random(20241115); // same seed = same anatomy
            for (int r = 0; r < 80; r++)
            {
                for (int c = 0; c < 80; c++)
                {
                    double dist = Math.Sqrt((r - 40.0) * (r - 40.0) + (c - 40.0) * (c - 40.0));
                    int baseVal;
                    if (dist < 15) baseVal = 2000;
                    else if (dist < 25) baseVal = 3500;
                    else if (dist < 35) baseVal = 1800;
                    else baseVal = 200;
                    rng.Next(-20, 21); // consume same rng to maintain anatomy
                    // High noise (low dose: 3x noise)
                    var rng2 = new Random(c * 80 + r + 1000);
                    int v = Math.Clamp(baseVal + rng2.Next(-200, 201), 0, 4095);
                    sw.Write(c < 79 ? $"{v} " : $"{v}");
                }
                sw.WriteLine();
            }
        }

        Assert.True(File.Exists(fullDosePath));
        Assert.True(File.Exists(lowDosePath));

        var fullDose = NetpbmImage.LoadFile(fullDosePath);
        var lowDose = NetpbmImage.LoadFile(lowDosePath);

        // GetNoiseEstimate
        var noiseFull = fullDose.GetNoiseEstimate();
        var noiseLow = lowDose.GetNoiseEstimate();
        Assert.True(noiseFull >= 0);
        Assert.True(noiseLow >= 0);
        Assert.Equal(noiseFull, fullDose.GetNoiseEstimate()); // consistent
        Assert.Equal(noiseLow, lowDose.GetNoiseEstimate());

        // Low-dose CT should have higher noise
        Assert.True(noiseLow >= noiseFull);

        // GetSignalToNoiseRatio
        var snrFull = fullDose.GetSignalToNoiseRatio();
        var snrLow = lowDose.GetSignalToNoiseRatio();
        Assert.True(snrFull >= 0);
        Assert.True(snrLow >= 0);
        Assert.Equal(snrFull, fullDose.GetSignalToNoiseRatio()); // consistent
        Assert.Equal(snrLow, lowDose.GetSignalToNoiseRatio());

        // Full-dose should have higher SNR
        Assert.True(snrFull >= snrLow);

        // Uniform "air" patch: zero noise
        var uniformPath = TempFile("ct_air_patch.pgm");
        using (var sw = new StreamWriter(uniformPath))
        {
            sw.WriteLine("P2");
            sw.WriteLine("40 40");
            sw.WriteLine("4095");
            for (int r = 0; r < 40; r++)
            {
                for (int c = 0; c < 40; c++)
                    sw.Write(c < 39 ? "200 " : "200");
                sw.WriteLine();
            }
        }
        var airPatch = NetpbmImage.LoadFile(uniformPath);
        Assert.Equal(0.0, airPatch.GetNoiseEstimate(), precision: 6);

        // Basic properties
        Assert.Equal(80, fullDose.Width);
        Assert.Equal(80, fullDose.Height);

        // SaveToFile and verify
        var outFull = TempFile("ct_full_dose_out.pgm");
        fullDose.SaveToFile(outFull);
        Assert.True(File.Exists(outFull));
        var loadedFull = NetpbmImage.LoadFile(outFull);
        Assert.Equal(noiseFull, loadedFull.GetNoiseEstimate(), precision: 6);
        Assert.Equal(snrFull, loadedFull.GetSignalToNoiseRatio(), precision: 6);

        // No-throw checks
        var ex1 = Record.Exception(() => loadedFull.GetNoiseEstimate());
        var ex2 = Record.Exception(() => loadedFull.GetSignalToNoiseRatio());
        var ex3 = Record.Exception(() => loadedFull.GetMeanIntensity());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
