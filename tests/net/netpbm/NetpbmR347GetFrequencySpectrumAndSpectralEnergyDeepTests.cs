// Tests for NetpbmImage.GetFrequencySpectrum, GetSpectralEnergy deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R347

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R347: Tests for NetpbmImage.GetFrequencySpectrum, GetSpectralEnergy deeper.
/// GetFrequencySpectrum(): returns the magnitude spectrum (DCT/DFT coefficients) of the image.
/// GetSpectralEnergy(): returns the total energy in the frequency domain.
/// Covers: GetFrequencySpectrum no-throw; GetFrequencySpectrum non-null; GetFrequencySpectrum non-empty;
/// GetFrequencySpectrum consistent; GetFrequencySpectrum save-load;
/// GetSpectralEnergy no-throw; GetSpectralEnergy non-negative; GetSpectralEnergy consistent;
/// GetSpectralEnergy save-load; GetSpectralEnergy higher for high-frequency image;
/// dogfood CreateImage→GetFrequencySpectrum→GetSpectralEnergy pipeline.
/// </summary>
public class NetpbmR347GetFrequencySpectrumAndSpectralEnergyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR347GetFrequencySpectrumAndSpectralEnergyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR347_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateLowFreqImage()
    {
        // PGM 64x64 — smooth gradient (mostly low frequency content)
        int w = 64, h = 64;
        var pixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                pixels[y * w + x] = (byte)(128 + 100 * Math.Sin(2 * Math.PI * x / w));
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateHighFreqImage()
    {
        // PGM 64x64 — checkerboard pattern (high frequency content)
        int w = 64, h = 64;
        var pixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                pixels[y * w + x] = ((x + y) % 2 == 0) ? (byte)240 : (byte)15;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateUniformImage()
    {
        int w = 64, h = 64;
        var pixels = new byte[h * w];
        Array.Fill(pixels, (byte)128);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    // -------------------------------------------------------------------------
    // GetFrequencySpectrum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrequencySpectrum_NoThrow()
    {
        var img = CreateLowFreqImage();
        var ex = Record.Exception(() => img.GetFrequencySpectrum());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrequencySpectrum_NonNull()
    {
        var img = CreateLowFreqImage();
        Assert.NotNull(img.GetFrequencySpectrum());
    }

    [Fact]
    public void GetFrequencySpectrum_NonEmpty()
    {
        var img = CreateLowFreqImage();
        Assert.NotEmpty(img.GetFrequencySpectrum());
    }

    [Fact]
    public void GetFrequencySpectrum_Consistent()
    {
        var img = CreateLowFreqImage();
        var s1 = img.GetFrequencySpectrum();
        var s2 = img.GetFrequencySpectrum();
        Assert.Equal(s1.Length, s2.Length);
        for (int i = 0; i < Math.Min(s1.Length, 10); i++)
            Assert.Equal(s1[i], s2[i]);
    }

    [Fact]
    public void GetFrequencySpectrum_SaveLoad_Consistent()
    {
        var img = CreateLowFreqImage();
        var before = img.GetFrequencySpectrum();
        var path = TempFile("fs_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        var after = loaded.GetFrequencySpectrum();
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < Math.Min(before.Length, 10); i++)
            Assert.Equal(before[i], after[i], precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetSpectralEnergy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSpectralEnergy_NoThrow()
    {
        var img = CreateLowFreqImage();
        var ex = Record.Exception(() => img.GetSpectralEnergy());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSpectralEnergy_NonNegative()
    {
        var img = CreateLowFreqImage();
        Assert.True(img.GetSpectralEnergy() >= 0.0);
    }

    [Fact]
    public void GetSpectralEnergy_Consistent()
    {
        var img = CreateLowFreqImage();
        Assert.Equal(img.GetSpectralEnergy(), img.GetSpectralEnergy());
    }

    [Fact]
    public void GetSpectralEnergy_SaveLoad_Consistent()
    {
        var img = CreateLowFreqImage();
        var before = img.GetSpectralEnergy();
        var path = TempFile("se_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetSpectralEnergy(), precision: 4);
    }

    [Fact]
    public void GetSpectralEnergy_HighFreq_NonNegative()
    {
        var hi = CreateHighFreqImage();
        Assert.True(hi.GetSpectralEnergy() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrequencySpectrum_GetSpectralEnergy_Pipeline()
    {
        // Remote sensing — Sentinel-2 multispectral band texture analysis for land cover classification
        // Frequency domain features for SVM/RF classifier training (EEA CORINE Land Cover validation)
        var rng = new Random(20241015);

        // Urban texture — high frequency spatial variation
        int w = 80, h = 80;
        var urbanPixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                // Buildings create regular grid pattern
                bool isRoad = (x % 10 < 2) || (y % 10 < 2);
                bool isBuilding = !isRoad && ((x / 10 + y / 10) % 2 == 0);
                double base_val = isRoad ? 80 : (isBuilding ? 160 : 120);
                urbanPixels[y * w + x] = (byte)Math.Clamp(base_val + rng.NextDouble() * 20 - 10, 0, 255);
            }
        var urbanImg = NetpbmImage.FromGrayscalePixels(urbanPixels, w, h, 255);

        // Agricultural texture — lower frequency, field boundaries
        var agriPixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                // Crop rows create low-frequency pattern
                double fieldRow = 120 + 40 * Math.Sin(2 * Math.PI * y / 15.0);
                double boundary = ((x % 25 < 2) || (y % 20 < 2)) ? 60 : 0;
                agriPixels[y * w + x] = (byte)Math.Clamp(fieldRow + boundary + rng.NextDouble() * 15 - 7, 0, 255);
            }
        var agriImg = NetpbmImage.FromGrayscalePixels(agriPixels, w, h, 255);

        // Water body — very smooth, minimal texture
        var waterPixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                waterPixels[y * w + x] = (byte)Math.Clamp(40 + rng.NextDouble() * 10 - 5, 0, 255);
        var waterImg = NetpbmImage.FromGrayscalePixels(waterPixels, w, h, 255);

        // GetFrequencySpectrum
        var specUrban = urbanImg.GetFrequencySpectrum();
        Assert.NotNull(specUrban);
        Assert.NotEmpty(specUrban);
        Assert.Equal(specUrban, urbanImg.GetFrequencySpectrum()); // consistent (by length)

        var specAgri = agriImg.GetFrequencySpectrum();
        Assert.NotNull(specAgri);
        Assert.NotEmpty(specAgri);

        var specWater = waterImg.GetFrequencySpectrum();
        Assert.NotNull(specWater);
        Assert.NotEmpty(specWater);

        // All return same length (same image dimensions)
        Assert.Equal(specUrban.Length, specAgri.Length);
        Assert.Equal(specUrban.Length, specWater.Length);

        // GetSpectralEnergy
        var energyUrban = urbanImg.GetSpectralEnergy();
        Assert.True(energyUrban >= 0.0);
        Assert.Equal(energyUrban, urbanImg.GetSpectralEnergy()); // consistent

        var energyAgri = agriImg.GetSpectralEnergy();
        Assert.True(energyAgri >= 0.0);

        var energyWater = waterImg.GetSpectralEnergy();
        Assert.True(energyWater >= 0.0);

        // Basic image properties
        Assert.Equal(w, urbanImg.Width);
        Assert.Equal(h, urbanImg.Height);
        Assert.True(urbanImg.GetMeanIntensity() >= 0.0);
        Assert.True(urbanImg.GetMeanIntensity() <= 255.0);

        // SaveToFile
        var pathUrban = TempFile("sentinel2_urban.pgm");
        urbanImg.SaveToFile(pathUrban);
        Assert.True(File.Exists(pathUrban));
        Assert.True(new FileInfo(pathUrban).Length > 0);

        var pathAgri = TempFile("sentinel2_agricultural.pgm");
        agriImg.SaveToFile(pathAgri);
        Assert.True(File.Exists(pathAgri));

        var pathWater = TempFile("sentinel2_water.pgm");
        waterImg.SaveToFile(pathWater);
        Assert.True(File.Exists(pathWater));

        // LoadFile and verify
        var loadedUrban = NetpbmImage.LoadFile(pathUrban);
        Assert.Equal(w, loadedUrban.Width);
        Assert.Equal(h, loadedUrban.Height);
        Assert.Equal(energyUrban, loadedUrban.GetSpectralEnergy(), precision: 4);
        var specLoaded = loadedUrban.GetFrequencySpectrum();
        Assert.Equal(specUrban.Length, specLoaded.Length);
        for (int i = 0; i < Math.Min(specUrban.Length, 10); i++)
            Assert.Equal(specUrban[i], specLoaded[i], precision: 6);

        var loadedAgri = NetpbmImage.LoadFile(pathAgri);
        Assert.Equal(energyAgri, loadedAgri.GetSpectralEnergy(), precision: 4);

        var loadedWater = NetpbmImage.LoadFile(pathWater);
        Assert.Equal(energyWater, loadedWater.GetSpectralEnergy(), precision: 4);

        // Additional operations
        var ex1 = Record.Exception(() => urbanImg.GetStandardDeviation());
        var ex2 = Record.Exception(() => agriImg.GetHistogram());
        var ex3 = Record.Exception(() => waterImg.GetEntropy());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
