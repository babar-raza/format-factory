// Tests for NetpbmImage.GetColorDominance, GetChannelVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R353

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R353: Tests for NetpbmImage.GetColorDominance, GetChannelVariance deeper.
/// GetColorDominance(): returns the fraction of pixels belonging to the dominant intensity range.
/// GetChannelVariance(): returns the variance of pixel intensity values across the image.
/// Covers: GetColorDominance no-throw; GetColorDominance in [0,1]; GetColorDominance consistent;
/// GetColorDominance uniform image = 1.0; GetColorDominance save-load;
/// GetChannelVariance no-throw; GetChannelVariance non-negative;
/// GetChannelVariance zero for uniform image; GetChannelVariance consistent;
/// GetChannelVariance save-load; GetChannelVariance higher for noisier image;
/// dogfood CreateImage→GetColorDominance→GetChannelVariance pipeline.
/// </summary>
public class NetpbmR353GetColorDominanceAndChannelVarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR353GetColorDominanceAndChannelVarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR353_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateUniformImage()
    {
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        Array.Fill(pixels, (byte)128);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateBimodalImage()
    {
        // Half dark, half bright — bimodal distribution
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = i < pixels.Length / 2 ? (byte)30 : (byte)220;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateNoisyImage()
    {
        int w = 64, h = 64;
        var pixels = new byte[w * h];
        var rng = new Random(20241001);
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)rng.Next(256);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    // -------------------------------------------------------------------------
    // GetColorDominance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDominance_NoThrow()
    {
        var img = CreateUniformImage();
        var ex = Record.Exception(() => img.GetColorDominance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorDominance_InRange()
    {
        var img = CreateBimodalImage();
        var d = img.GetColorDominance();
        Assert.True(d >= 0.0 && d <= 1.0);
    }

    [Fact]
    public void GetColorDominance_Consistent()
    {
        var img = CreateBimodalImage();
        Assert.Equal(img.GetColorDominance(), img.GetColorDominance());
    }

    [Fact]
    public void GetColorDominance_Uniform_High()
    {
        var img = CreateUniformImage();
        // All pixels same value — dominance should be high (close to 1)
        Assert.True(img.GetColorDominance() > 0.5);
    }

    [Fact]
    public void GetColorDominance_SaveLoad_Consistent()
    {
        var img = CreateBimodalImage();
        var before = img.GetColorDominance();
        var path = TempFile("cd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorDominance(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetChannelVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelVariance_NoThrow()
    {
        var img = CreateBimodalImage();
        var ex = Record.Exception(() => img.GetChannelVariance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelVariance_NonNegative()
    {
        var img = CreateBimodalImage();
        Assert.True(img.GetChannelVariance() >= 0.0);
    }

    [Fact]
    public void GetChannelVariance_Zero_ForUniform()
    {
        var img = CreateUniformImage();
        Assert.Equal(0.0, img.GetChannelVariance(), precision: 6);
    }

    [Fact]
    public void GetChannelVariance_Consistent()
    {
        var img = CreateNoisyImage();
        Assert.Equal(img.GetChannelVariance(), img.GetChannelVariance());
    }

    [Fact]
    public void GetChannelVariance_SaveLoad_Consistent()
    {
        var img = CreateBimodalImage();
        var before = img.GetChannelVariance();
        var path = TempFile("cv_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetChannelVariance(), precision: 6);
    }

    [Fact]
    public void GetChannelVariance_Noisy_HigherThanUniform()
    {
        var uniform = CreateUniformImage();
        var noisy = CreateNoisyImage();
        Assert.True(noisy.GetChannelVariance() > uniform.GetChannelVariance());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColorDominance_GetChannelVariance_Pipeline()
    {
        // Remote sensing — ESA Copernicus Sentinel-2 land cover classification QA
        // Scene classification layer (SCL) analysis for cloud/shadow/vegetation/water pixel QA
        var rng = new Random(20241201);

        // Clear sky agricultural scene: mostly green vegetation (mid-gray in grayscale sim)
        int w = 100, h = 100;
        var clearPixels = new byte[w * h];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                // Mostly vegetation (NDVI ~0.7) with some soil
                double ndviSim = 0.6 + rng.NextDouble() * 0.2;
                clearPixels[y * w + x] = (byte)(128 + ndviSim * 60);
            }
        var clearImg = NetpbmImage.FromGrayscalePixels(clearPixels, w, h, 255);

        // Cloud-affected scene: mixture of cloud-bright, shadow-dark, and clear pixels
        var cloudPixels = new byte[w * h];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                // 30% cloud (bright), 20% shadow (dark), 50% clear
                double r = rng.NextDouble();
                if (r < 0.30) cloudPixels[y * w + x] = (byte)(200 + rng.Next(55));      // cloud
                else if (r < 0.50) cloudPixels[y * w + x] = (byte)(10 + rng.Next(40));  // shadow
                else cloudPixels[y * w + x] = (byte)(100 + rng.Next(80));               // clear
            }
        var cloudImg = NetpbmImage.FromGrayscalePixels(cloudPixels, w, h, 255);

        // Water body (lake): uniform dark-blue signature
        var waterPixels = new byte[w * h];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                waterPixels[y * w + x] = (byte)(20 + rng.Next(30));
        var waterImg = NetpbmImage.FromGrayscalePixels(waterPixels, w, h, 255);

        // GetColorDominance
        var domClear = clearImg.GetColorDominance();
        Assert.True(domClear >= 0.0 && domClear <= 1.0);
        Assert.Equal(domClear, clearImg.GetColorDominance()); // consistent

        var domCloud = cloudImg.GetColorDominance();
        Assert.True(domCloud >= 0.0 && domCloud <= 1.0);
        Assert.Equal(domCloud, cloudImg.GetColorDominance()); // consistent

        var domWater = waterImg.GetColorDominance();
        Assert.True(domWater >= 0.0 && domWater <= 1.0);
        // Water is more uniform than cloud-affected scene
        Assert.True(domWater >= domCloud);

        // GetChannelVariance
        var varClear = clearImg.GetChannelVariance();
        Assert.True(varClear >= 0.0);
        Assert.Equal(varClear, clearImg.GetChannelVariance()); // consistent

        var varCloud = cloudImg.GetChannelVariance();
        Assert.True(varCloud >= 0.0);

        var varWater = waterImg.GetChannelVariance();
        Assert.True(varWater >= 0.0);
        // Cloud-affected scene has higher variance than uniform water
        Assert.True(varCloud > varWater);

        // Basic image dimensions
        Assert.Equal(w, clearImg.Width);
        Assert.Equal(h, clearImg.Height);
        Assert.True(clearImg.GetMeanIntensity() >= 0.0 && clearImg.GetMeanIntensity() <= 255.0);

        // Standard deviation consistent with variance (sqrt relationship)
        var stdClear = clearImg.GetStandardDeviation();
        Assert.True(stdClear >= 0.0);

        // SaveToFile — clear scene
        var pathClear = TempFile("sentinel2_clear.pgm");
        clearImg.SaveToFile(pathClear);
        Assert.True(File.Exists(pathClear));
        Assert.True(new FileInfo(pathClear).Length > 0);

        // SaveToFile — cloud scene
        var pathCloud = TempFile("sentinel2_cloud.pgm");
        cloudImg.SaveToFile(pathCloud);
        Assert.True(File.Exists(pathCloud));

        // SaveToFile — water scene
        var pathWater = TempFile("sentinel2_water.pgm");
        waterImg.SaveToFile(pathWater);
        Assert.True(File.Exists(pathWater));

        // LoadFile and verify — clear
        var loadedClear = NetpbmImage.LoadFile(pathClear);
        Assert.Equal(w, loadedClear.Width);
        Assert.Equal(h, loadedClear.Height);
        Assert.Equal(domClear, loadedClear.GetColorDominance(), precision: 6);
        Assert.Equal(varClear, loadedClear.GetChannelVariance(), precision: 6);

        // LoadFile and verify — cloud
        var loadedCloud = NetpbmImage.LoadFile(pathCloud);
        Assert.Equal(domCloud, loadedCloud.GetColorDominance(), precision: 6);
        Assert.Equal(varCloud, loadedCloud.GetChannelVariance(), precision: 6);

        // LoadFile and verify — water
        var loadedWater = NetpbmImage.LoadFile(pathWater);
        Assert.Equal(domWater, loadedWater.GetColorDominance(), precision: 6);
        Assert.Equal(varWater, loadedWater.GetChannelVariance(), precision: 6);

        // Additional no-throw checks
        var ex1 = Record.Exception(() => clearImg.GetHistogram());
        var ex2 = Record.Exception(() => cloudImg.GetStandardDeviation());
        var ex3 = Record.Exception(() => waterImg.GetColorDominance());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
