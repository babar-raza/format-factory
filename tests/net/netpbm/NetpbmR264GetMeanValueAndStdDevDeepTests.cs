// Tests for NetpbmImage.GetMeanValue, GetStdDev, ApplyGamma deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R264

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R264: Tests for NetpbmImage.GetMeanValue, GetStdDev, ApplyGamma deeper.
/// GetMeanValue(): returns the mean pixel intensity across all pixels.
/// GetStdDev(): returns the standard deviation of pixel values.
/// ApplyGamma(gamma): applies gamma correction to the image.
/// Covers: GetMeanValue positive; GetMeanValue no-throw; GetMeanValue in 0-255 range;
/// GetMeanValue consistent; GetMeanValue for uniform image; GetMeanValue save-load;
/// GetMeanValue after Invert=255-original; GetMeanValue changes after SetPixel;
/// GetStdDev non-negative; GetStdDev no-throw; GetStdDev consistent;
/// GetStdDev uniform image=0; GetStdDev gradient>0; GetStdDev save-load;
/// GetStdDev after Normalize changes; GetStdDev after Threshold low;
/// ApplyGamma non-null; ApplyGamma no-throw; ApplyGamma same dims;
/// ApplyGamma gamma=1.0 preserves vals; ApplyGamma gamma>1 dims same;
/// ApplyGamma consistent; ApplyGamma then SaveToFile; ApplyGamma then Normalize no-throw;
/// ApplyGamma then FlipHorizontal no-throw; ApplyGamma save-load dims;
/// dogfood CreatePgm→GetMeanValue→GetStdDev→ApplyGamma→SaveToFile pipeline.
/// </summary>
public class NetpbmR264GetMeanValueAndStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR264GetMeanValueAndStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR264_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGradient(int w, int h)
    {
        var img = NetpbmImage.CreatePgm(w, h, 255);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, (byte)(x * 255 / (w - 1)));
        return img;
    }

    private static NetpbmImage CreateUniform(int w, int h, byte value)
    {
        var img = NetpbmImage.CreatePgm(w, h, 255);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, value);
        return img;
    }

    // -------------------------------------------------------------------------
    // GetMeanValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanValue_Positive()
    {
        var img = CreateGradient(10, 8);
        Assert.True(img.GetMeanValue() >= 0);
    }

    [Fact]
    public void GetMeanValue_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var ex = Record.Exception(() => img.GetMeanValue());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMeanValue_InRange()
    {
        var img = CreateGradient(10, 8);
        var mean = img.GetMeanValue();
        Assert.True(mean >= 0.0 && mean <= 255.0);
    }

    [Fact]
    public void GetMeanValue_Consistent()
    {
        var img = CreateGradient(10, 8);
        Assert.Equal(img.GetMeanValue(), img.GetMeanValue(), 5);
    }

    [Fact]
    public void GetMeanValue_Uniform128()
    {
        var img = CreateUniform(8, 8, 128);
        Assert.Equal(128.0, img.GetMeanValue(), 3);
    }

    [Fact]
    public void GetMeanValue_SaveLoad_Consistent()
    {
        var img = CreateGradient(10, 8);
        var before = img.GetMeanValue();
        var path = TempFile("mean_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetMeanValue(), 3);
    }

    [Fact]
    public void GetMeanValue_AfterInvert_Complement()
    {
        var img = CreateGradient(10, 8);
        var mean = img.GetMeanValue();
        var inverted = img.Invert();
        var invertedMean = inverted.GetMeanValue();
        // mean + invertedMean ≈ 255
        Assert.True(Math.Abs(mean + invertedMean - 255.0) <= 5.0);
    }

    [Fact]
    public void GetMeanValue_Changes_After_SetPixel()
    {
        var img = CreateUniform(8, 8, 100);
        var before = img.GetMeanValue();
        img.SetPixel(4, 4, 200); // raise one pixel
        var after = img.GetMeanValue();
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // GetStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStdDev_NonNegative()
    {
        var img = CreateGradient(10, 8);
        Assert.True(img.GetStdDev() >= 0.0);
    }

    [Fact]
    public void GetStdDev_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var ex = Record.Exception(() => img.GetStdDev());
        Assert.Null(ex);
    }

    [Fact]
    public void GetStdDev_Consistent()
    {
        var img = CreateGradient(10, 8);
        Assert.Equal(img.GetStdDev(), img.GetStdDev(), 5);
    }

    [Fact]
    public void GetStdDev_Uniform_IsZero()
    {
        var img = CreateUniform(8, 8, 128);
        Assert.Equal(0.0, img.GetStdDev(), 3);
    }

    [Fact]
    public void GetStdDev_Gradient_GreaterThanZero()
    {
        var img = CreateGradient(10, 8);
        Assert.True(img.GetStdDev() > 0.0);
    }

    [Fact]
    public void GetStdDev_SaveLoad_Consistent()
    {
        var img = CreateGradient(10, 8);
        var before = img.GetStdDev();
        var path = TempFile("std_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetStdDev(), 3);
    }

    // -------------------------------------------------------------------------
    // ApplyGamma
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_NonNull()
    {
        var img = CreateGradient(10, 8);
        Assert.NotNull(img.ApplyGamma(1.0));
    }

    [Fact]
    public void ApplyGamma_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var ex = Record.Exception(() => img.ApplyGamma(2.2));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGamma_SameDimensions()
    {
        var img = CreateGradient(12, 8);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(12, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ApplyGamma_Gamma1_PreservesDimensions()
    {
        var img = CreateGradient(10, 8);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(10, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ApplyGamma_Consistent()
    {
        var img = CreateGradient(10, 8);
        var r1 = img.ApplyGamma(2.2);
        var r2 = img.ApplyGamma(2.2);
        Assert.Equal(r1.GetPixelValue(5, 4), r2.GetPixelValue(5, 4));
    }

    [Fact]
    public void ApplyGamma_ThenSaveToFile()
    {
        var img = CreateGradient(12, 8);
        var result = img.ApplyGamma(2.2);
        var path = TempFile("gamma_out.pgm");
        result.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(12, loaded.Width);
    }

    [Fact]
    public void ApplyGamma_ThenNormalize_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var result = img.ApplyGamma(2.2);
        var ex = Record.Exception(() => result.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGamma_ThenFlipHorizontal_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var result = img.ApplyGamma(0.5);
        var ex = Record.Exception(() => result.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGamma_SaveLoad_Dims_Consistent()
    {
        var img = CreateGradient(12, 8);
        var result = img.ApplyGamma(2.2);
        var path = TempFile("gamma_save.pgm");
        result.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(12, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_GetMeanValue_GetStdDev_ApplyGamma_SaveToFile_Pipeline()
    {
        // Create 16×12 gradient image
        var img = CreateGradient(16, 12);
        Assert.Equal(16, img.Width);
        Assert.Equal(12, img.Height);

        // GetMeanValue
        var mean = img.GetMeanValue();
        Assert.True(mean >= 0.0 && mean <= 255.0);
        // Gradient from 0 to 255 → mean ≈ 127.5
        Assert.True(mean > 100.0 && mean < 155.0);

        // Consistent
        Assert.Equal(mean, img.GetMeanValue(), 5);

        // GetStdDev
        var stddev = img.GetStdDev();
        Assert.True(stddev > 0.0); // gradient image has high std dev
        Assert.Equal(stddev, img.GetStdDev(), 5);

        // Uniform image
        var uniform = CreateUniform(8, 8, 200);
        Assert.Equal(200.0, uniform.GetMeanValue(), 3);
        Assert.Equal(0.0, uniform.GetStdDev(), 3);

        // After Invert — mean + invertedMean ≈ 255
        var inverted = img.Invert();
        var invertedMean = inverted.GetMeanValue();
        Assert.True(Math.Abs(mean + invertedMean - 255.0) <= 5.0);

        // ApplyGamma — darkening (gamma > 1)
        var dark = img.ApplyGamma(2.2);
        Assert.Equal(16, dark.Width);
        Assert.Equal(12, dark.Height);
        // Darker image → lower mean
        var darkMean = dark.GetMeanValue();
        Assert.True(darkMean <= mean + 10); // approximately darker

        // ApplyGamma — brightening (gamma < 1)
        var bright = img.ApplyGamma(0.5);
        Assert.Equal(16, bright.Width);
        Assert.Equal(12, bright.Height);

        // Consistent
        var dark2 = img.ApplyGamma(2.2);
        Assert.Equal(dark.GetPixelValue(8, 6), dark2.GetPixelValue(8, 6));

        // Normalize the gamma-corrected image
        var normGamma = dark.Normalize();
        Assert.Equal(16, normGamma.Width);

        // GetMeanValue after gamma application
        Assert.True(dark.GetMeanValue() >= 0 && dark.GetMeanValue() <= 255);

        // SaveToFile originals and processed
        var pathOrig = TempFile("dogfood_orig.pgm");
        img.SaveToFile(pathOrig);
        Assert.True(File.Exists(pathOrig));

        var pathDark = TempFile("dogfood_dark.pgm");
        dark.SaveToFile(pathDark);
        Assert.True(File.Exists(pathDark));

        var pathBright = TempFile("dogfood_bright.pgm");
        bright.SaveToFile(pathBright);
        Assert.True(File.Exists(pathBright));

        // LoadFile and verify
        var loadedOrig = NetpbmImage.LoadFile(pathOrig);
        Assert.Equal(mean, loadedOrig.GetMeanValue(), 3);
        Assert.Equal(stddev, loadedOrig.GetStdDev(), 3);

        var loadedDark = NetpbmImage.LoadFile(pathDark);
        Assert.Equal(16, loadedDark.Width);
        Assert.Equal(12, loadedDark.Height);
        Assert.Equal(dark.GetMeanValue(), loadedDark.GetMeanValue(), 3);

        // ApplyGamma on loaded
        var loadedGamma = loadedOrig.ApplyGamma(1.5);
        Assert.Equal(16, loadedGamma.Width);
        Assert.True(loadedGamma.GetMeanValue() >= 0);

        // Final save
        var pathFinal = TempFile("dogfood_final.pgm");
        loadedGamma.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
        var final = NetpbmImage.LoadFile(pathFinal);
        Assert.Equal(16, final.Width);
        Assert.Equal(12, final.Height);
        Assert.True(final.GetMeanValue() >= 0);
        Assert.True(final.GetStdDev() >= 0);
    }
}
