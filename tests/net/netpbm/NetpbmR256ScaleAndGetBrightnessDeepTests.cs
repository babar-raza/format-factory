// Tests for NetpbmImage.Scale, GetBrightness, GetContrast deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R256

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R256: Tests for NetpbmImage.Scale, GetBrightness, GetContrast deeper.
/// Scale(factor): scales the image by a given factor (e.g. 2.0 = double size).
/// GetBrightness(): returns the average pixel intensity (0-255).
/// GetContrast(): returns the standard deviation of pixel intensities.
/// Covers: Scale2_DoublesDims; Scale0.5_HalvesDims; Scale1_SameDims;
/// Scale no-throw; Scale then Crop no-throw; Scale then Rotate no-throw;
/// Scale then Invert no-throw; Scale save-load consistent;
/// Scale then GetBrightness consistent; Scale non-null; Scale non-zero dims;
/// GetBrightness in range; GetBrightness for white>=200; GetBrightness for black<=10;
/// GetBrightness consistent; GetBrightness no-throw; GetBrightness after Invert changes;
/// GetBrightness after SetPixel updates; GetBrightness save-load approx;
/// GetContrast non-negative; GetContrast for uniform=0; GetContrast for gradient>0;
/// GetContrast consistent; GetContrast no-throw; GetContrast after Invert similar;
/// GetContrast save-load consistent;
/// dogfood CreatePgm→Scale→GetBrightness→GetContrast→SaveToFile pipeline.
/// </summary>
public class NetpbmR256ScaleAndGetBrightnessDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR256ScaleAndGetBrightnessDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR256_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayGradient(int width, int height)
    {
        var img = NetpbmImage.CreatePgm(width, height, 255);
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                img.SetPixel(x, y, (byte)((x + y) * 255 / (width + height - 2)));
        return img;
    }

    // -------------------------------------------------------------------------
    // Scale
    // -------------------------------------------------------------------------

    [Fact]
    public void Scale2_DoublesDimensions()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(2.0);
        Assert.Equal(16, scaled.Width);
        Assert.Equal(12, scaled.Height);
    }

    [Fact]
    public void Scale05_HalvesDimensions()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(0.5);
        Assert.Equal(4, scaled.Width);
        Assert.Equal(3, scaled.Height);
    }

    [Fact]
    public void Scale1_SameDimensions()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(1.0);
        Assert.Equal(8, scaled.Width);
        Assert.Equal(6, scaled.Height);
    }

    [Fact]
    public void Scale_NonNull()
    {
        var img = CreateGrayGradient(8, 6);
        Assert.NotNull(img.Scale(2.0));
    }

    [Fact]
    public void Scale_NoThrow()
    {
        var img = CreateGrayGradient(8, 6);
        var ex = Record.Exception(() => img.Scale(2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void Scale_NonZeroDimensions()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(1.5);
        Assert.True(scaled.Width > 0);
        Assert.True(scaled.Height > 0);
    }

    [Fact]
    public void Scale_ThenCrop_NoThrow()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(2.0);
        var ex = Record.Exception(() => scaled.Crop(0, 0, 4, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void Scale_ThenRotate_NoThrow()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(2.0);
        var ex = Record.Exception(() => scaled.Rotate(90));
        Assert.Null(ex);
    }

    [Fact]
    public void Scale_ThenInvert_NoThrow()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(2.0);
        var ex = Record.Exception(() => scaled.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void Scale_SaveLoad_ConsistentDimensions()
    {
        var img = CreateGrayGradient(8, 6);
        var scaled = img.Scale(2.0);
        var path = TempFile("scaled.pgm");
        scaled.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(16, loaded.Width);
        Assert.Equal(12, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_InRange()
    {
        var img = CreateGrayGradient(8, 6);
        var b = img.GetBrightness();
        Assert.True(b >= 0.0 && b <= 255.0);
    }

    [Fact]
    public void GetBrightness_ForWhite_HighValue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 255);
        Assert.True(img.GetBrightness() >= 200.0);
    }

    [Fact]
    public void GetBrightness_ForBlack_LowValue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 0);
        Assert.True(img.GetBrightness() <= 10.0);
    }

    [Fact]
    public void GetBrightness_Consistent()
    {
        var img = CreateGrayGradient(8, 6);
        Assert.Equal(img.GetBrightness(), img.GetBrightness());
    }

    [Fact]
    public void GetBrightness_NoThrow()
    {
        var img = CreateGrayGradient(8, 6);
        var ex = Record.Exception(() => img.GetBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightness_AfterInvert_Changes()
    {
        var img = CreateGrayGradient(8, 6);
        var orig = img.GetBrightness();
        var inverted = img.Invert();
        var invBright = inverted.GetBrightness();
        Assert.NotEqual(orig, invBright);
    }

    [Fact]
    public void GetBrightness_AfterSetPixel_Updates()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 100);
        var before = img.GetBrightness();
        // Set all to 200 — brightness should increase
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 200);
        Assert.True(img.GetBrightness() > before);
    }

    [Fact]
    public void GetBrightness_SaveLoad_Approx()
    {
        var img = CreateGrayGradient(8, 6);
        var orig = img.GetBrightness();
        var path = TempFile("brightness_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.True(Math.Abs(loaded.GetBrightness() - orig) <= 5.0);
    }

    // -------------------------------------------------------------------------
    // GetContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrast_NonNegative()
    {
        var img = CreateGrayGradient(8, 6);
        Assert.True(img.GetContrast() >= 0.0);
    }

    [Fact]
    public void GetContrast_ForUniform_IsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 128);
        // Uniform image has zero contrast (std dev = 0)
        Assert.True(img.GetContrast() <= 1.0); // allow tiny floating point error
    }

    [Fact]
    public void GetContrast_ForGradient_Positive()
    {
        var img = CreateGrayGradient(8, 8);
        Assert.True(img.GetContrast() > 0.0);
    }

    [Fact]
    public void GetContrast_Consistent()
    {
        var img = CreateGrayGradient(8, 6);
        Assert.Equal(img.GetContrast(), img.GetContrast());
    }

    [Fact]
    public void GetContrast_NoThrow()
    {
        var img = CreateGrayGradient(8, 6);
        var ex = Record.Exception(() => img.GetContrast());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrast_SaveLoad_Approx()
    {
        var img = CreateGrayGradient(8, 6);
        var orig = img.GetContrast();
        var path = TempFile("contrast_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.True(Math.Abs(loaded.GetContrast() - orig) <= 2.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_Scale_GetBrightness_GetContrast_SaveToFile_Pipeline()
    {
        // Create 12×8 gradient image (0..255 range)
        var img = NetpbmImage.CreatePgm(12, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 12; x++)
                img.SetPixel(x, y, (byte)((x + y) * 255 / 18));

        Assert.Equal(12, img.Width);
        Assert.Equal(8, img.Height);

        // GetBrightness baseline — gradient image ~mid-range
        var brightness = img.GetBrightness();
        Assert.True(brightness >= 0.0 && brightness <= 255.0);
        Assert.Equal(brightness, img.GetBrightness()); // consistent

        // GetContrast baseline — gradient has significant contrast
        var contrast = img.GetContrast();
        Assert.True(contrast > 0.0);
        Assert.Equal(contrast, img.GetContrast()); // consistent

        // Scale 2x
        var scaled2x = img.Scale(2.0);
        Assert.Equal(24, scaled2x.Width);
        Assert.Equal(16, scaled2x.Height);

        // GetBrightness on scaled should be similar (scaling doesn't change avg brightness)
        var scaledBrightness = scaled2x.GetBrightness();
        Assert.True(Math.Abs(scaledBrightness - brightness) <= 20.0); // within 20 units

        // Scale 0.5x
        var scaled05x = img.Scale(0.5);
        Assert.Equal(6, scaled05x.Width);
        Assert.Equal(4, scaled05x.Height);

        // Scale 1.0x — same dims
        var scaled1x = img.Scale(1.0);
        Assert.Equal(12, scaled1x.Width);
        Assert.Equal(8, scaled1x.Height);

        // GetContrast on scaled2x > 0
        Assert.True(scaled2x.GetContrast() > 0.0);

        // Invert and verify brightness changes
        var inverted = img.Invert();
        var invertedBrightness = inverted.GetBrightness();
        Assert.NotEqual(brightness, invertedBrightness);
        // For gradient 0-255, invert flips to 255-0, so brightness should sum to ~255
        Assert.True(Math.Abs(brightness + invertedBrightness - 255.0) <= 20.0);

        // GetContrast after Invert — same distribution, same std dev
        var invertedContrast = inverted.GetContrast();
        Assert.True(Math.Abs(invertedContrast - contrast) <= 2.0);

        // Uniform image for contrast=0 check
        var uniform = NetpbmImage.CreatePgm(8, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                uniform.SetPixel(x, y, 128);
        Assert.True(uniform.GetContrast() <= 1.0);
        Assert.True(Math.Abs(uniform.GetBrightness() - 128.0) <= 1.0);

        // White image
        var white = NetpbmImage.CreatePgm(4, 4, 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                white.SetPixel(x, y, 255);
        Assert.True(white.GetBrightness() >= 200.0);
        Assert.True(white.GetContrast() <= 1.0);

        // Scale then Crop
        var cropped = scaled2x.Crop(0, 0, 8, 8);
        Assert.Equal(8, cropped.Width);
        Assert.Equal(8, cropped.Height);
        Assert.True(cropped.GetBrightness() >= 0.0);
        Assert.True(cropped.GetContrast() >= 0.0);

        // SaveToFile multiple images
        var pathOrig = TempFile("dogfood_orig.pgm");
        img.SaveToFile(pathOrig);
        Assert.True(File.Exists(pathOrig));

        var pathScaled2x = TempFile("dogfood_scaled2x.pgm");
        scaled2x.SaveToFile(pathScaled2x);
        Assert.True(File.Exists(pathScaled2x));

        var pathScaled05x = TempFile("dogfood_scaled05x.pgm");
        scaled05x.SaveToFile(pathScaled05x);
        Assert.True(File.Exists(pathScaled05x));

        // LoadFile and verify
        var loadedOrig = NetpbmImage.LoadFile(pathOrig);
        Assert.Equal(12, loadedOrig.Width);
        Assert.Equal(8, loadedOrig.Height);
        Assert.True(Math.Abs(loadedOrig.GetBrightness() - brightness) <= 5.0);

        var loadedScaled = NetpbmImage.LoadFile(pathScaled2x);
        Assert.Equal(24, loadedScaled.Width);
        Assert.Equal(16, loadedScaled.Height);

        // Scale loaded image
        var rescaled = loadedOrig.Scale(3.0);
        Assert.Equal(36, rescaled.Width);
        Assert.Equal(24, rescaled.Height);
        Assert.True(rescaled.GetBrightness() >= 0.0);

        // Final SaveToFile
        var pathFinal = TempFile("dogfood_final.pgm");
        rescaled.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
    }
}
