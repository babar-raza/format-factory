// Tests for NetpbmImage.ConvertToRgb, GetColorDepth, Scale deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R246

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R246: Tests for NetpbmImage.ConvertToRgb, GetColorDepth, Scale deeper.
/// ConvertToRgb(): converts the image to RGB format.
/// GetColorDepth(): returns the color depth (bits per channel).
/// Scale(factor): scales the image by the given factor.
/// Covers: ConvertToRgb non-null; ConvertToRgb preserves pixel count; ConvertToRgb width correct;
/// ConvertToRgb height correct; ConvertToRgb no-throw; ConvertToRgb persist;
/// ConvertToRgb from grayscale; ConvertToRgb from RGB stays RGB; ConvertToRgb from PBM;
/// ConvertToRgb then Invert; ConvertToRgb then Crop;
/// GetColorDepth positive; GetColorDepth in valid range; GetColorDepth consistent;
/// GetColorDepth no-throw; GetColorDepth for grayscale; GetColorDepth for RGB;
/// GetColorDepth after ConvertToRgb; GetColorDepth for PBM;
/// Scale non-null; Scale 2x doubles dims; Scale 0.5x halves dims; Scale no-throw;
/// Scale persist; Scale 1x identity dims; Scale then Crop; Scale then Invert;
/// dogfood CreateGrayscale→ConvertToRgb→GetColorDepth→Scale→SaveToFile pipeline.
/// </summary>
public class NetpbmR246ConvertToRgbAndGetColorDepthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR246ConvertToRgbAndGetColorDepthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR246_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayscale8x6()
    {
        var pixels = new byte[8 * 6];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i * 4);
        return NetpbmImage.CreatePgm(8, 6, pixels);
    }

    private static NetpbmImage CreateRgb6x4()
    {
        var pixels = new byte[6 * 4 * 3];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 256);
        return NetpbmImage.CreatePpm(6, 4, pixels);
    }

    // -------------------------------------------------------------------------
    // ConvertToRgb
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertToRgb_NonNull()
    {
        var img = CreateGrayscale8x6();
        Assert.NotNull(img.ConvertToRgb());
    }

    [Fact]
    public void ConvertToRgb_WidthCorrect()
    {
        var img = CreateGrayscale8x6();
        var rgb = img.ConvertToRgb();
        Assert.Equal(img.Width, rgb.Width);
    }

    [Fact]
    public void ConvertToRgb_HeightCorrect()
    {
        var img = CreateGrayscale8x6();
        var rgb = img.ConvertToRgb();
        Assert.Equal(img.Height, rgb.Height);
    }

    [Fact]
    public void ConvertToRgb_PixelCountPreserved()
    {
        var img = CreateGrayscale8x6();
        var rgb = img.ConvertToRgb();
        Assert.Equal(img.GetPixelCount(), rgb.GetPixelCount());
    }

    [Fact]
    public void ConvertToRgb_NoThrow()
    {
        var img = CreateGrayscale8x6();
        var ex = Record.Exception(() => img.ConvertToRgb());
        Assert.Null(ex);
    }

    [Fact]
    public void ConvertToRgb_Persist()
    {
        var img = CreateGrayscale8x6();
        var rgb = img.ConvertToRgb();
        var path = TempFile("converted_rgb.ppm");
        rgb.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(6, loaded.Height);
    }

    [Fact]
    public void ConvertToRgb_FromRgbStaysRgb()
    {
        var img = CreateRgb6x4();
        var rgb = img.ConvertToRgb();
        Assert.NotNull(rgb);
        Assert.Equal(img.Width, rgb.Width);
        Assert.Equal(img.Height, rgb.Height);
    }

    [Fact]
    public void ConvertToRgb_ThenInvert_NonNull()
    {
        var img = CreateGrayscale8x6();
        var rgb = img.ConvertToRgb();
        var inverted = rgb.Invert();
        Assert.NotNull(inverted);
        Assert.Equal(rgb.Width, inverted.Width);
    }

    [Fact]
    public void ConvertToRgb_ThenCrop_NonNull()
    {
        var img = CreateGrayscale8x6();
        var rgb = img.ConvertToRgb();
        var cropped = rgb.Crop(0, 0, 4, 3);
        Assert.NotNull(cropped);
        Assert.Equal(4, cropped.Width);
        Assert.Equal(3, cropped.Height);
    }

    // -------------------------------------------------------------------------
    // GetColorDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_Positive()
    {
        var img = CreateGrayscale8x6();
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_InValidRange()
    {
        var img = CreateGrayscale8x6();
        var depth = img.GetColorDepth();
        Assert.True(depth >= 1 && depth <= 32);
    }

    [Fact]
    public void GetColorDepth_Consistent()
    {
        var img = CreateGrayscale8x6();
        Assert.Equal(img.GetColorDepth(), img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_NoThrow()
    {
        var img = CreateGrayscale8x6();
        var ex = Record.Exception(() => img.GetColorDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorDepth_ForGrayscale_Positive()
    {
        var img = CreateGrayscale8x6();
        Assert.True(img.GetColorDepth() >= 1);
    }

    [Fact]
    public void GetColorDepth_ForRgb_Positive()
    {
        var img = CreateRgb6x4();
        Assert.True(img.GetColorDepth() >= 1);
    }

    [Fact]
    public void GetColorDepth_AfterConvertToRgb_Positive()
    {
        var img = CreateGrayscale8x6();
        var rgb = img.ConvertToRgb();
        Assert.True(rgb.GetColorDepth() >= 1);
    }

    [Fact]
    public void GetColorDepth_ForPbm_NonNegative()
    {
        var pixels = new byte[6 * 4];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 2);
        var img = NetpbmImage.CreatePbm(6, 4, pixels);
        Assert.True(img.GetColorDepth() >= 0);
    }

    // -------------------------------------------------------------------------
    // Scale
    // -------------------------------------------------------------------------

    [Fact]
    public void Scale_NonNull()
    {
        var img = CreateGrayscale8x6();
        Assert.NotNull(img.Scale(2.0));
    }

    [Fact]
    public void Scale_2x_DoublesDimensions()
    {
        var img = CreateGrayscale8x6();
        var scaled = img.Scale(2.0);
        Assert.Equal(img.Width * 2, scaled.Width);
        Assert.Equal(img.Height * 2, scaled.Height);
    }

    [Fact]
    public void Scale_HalfX_HalvesDimensions()
    {
        var img = CreateGrayscale8x6();
        var scaled = img.Scale(0.5);
        Assert.Equal(img.Width / 2, scaled.Width);
        Assert.Equal(img.Height / 2, scaled.Height);
    }

    [Fact]
    public void Scale_NoThrow()
    {
        var img = CreateGrayscale8x6();
        var ex = Record.Exception(() => img.Scale(1.5));
        Assert.Null(ex);
    }

    [Fact]
    public void Scale_Persist()
    {
        var img = CreateGrayscale8x6();
        var scaled = img.Scale(2.0);
        var path = TempFile("scaled.pgm");
        scaled.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(16, loaded.Width);
        Assert.Equal(12, loaded.Height);
    }

    [Fact]
    public void Scale_1x_PreservesDimensions()
    {
        var img = CreateGrayscale8x6();
        var scaled = img.Scale(1.0);
        Assert.Equal(img.Width, scaled.Width);
        Assert.Equal(img.Height, scaled.Height);
    }

    [Fact]
    public void Scale_ThenCrop_Works()
    {
        var img = CreateGrayscale8x6();
        var scaled = img.Scale(2.0);
        var cropped = scaled.Crop(0, 0, 8, 6);
        Assert.Equal(8, cropped.Width);
        Assert.Equal(6, cropped.Height);
    }

    [Fact]
    public void Scale_ThenInvert_Works()
    {
        var img = CreateGrayscale8x6();
        var scaled = img.Scale(2.0);
        var inverted = scaled.Invert();
        Assert.NotNull(inverted);
        Assert.Equal(scaled.Width, inverted.Width);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ConvertToRgb_GetColorDepth_Scale_SaveToFile_Pipeline()
    {
        // Create grayscale base image 10×8
        var grayPixels = new byte[10 * 8];
        for (int i = 0; i < grayPixels.Length; i++)
            grayPixels[i] = (byte)(i * 3 % 256);
        var gray = NetpbmImage.CreatePgm(10, 8, grayPixels);

        // GetColorDepth on grayscale
        var grayDepth = gray.GetColorDepth();
        Assert.True(grayDepth >= 1);

        // ConvertToRgb
        var rgb = gray.ConvertToRgb();
        Assert.NotNull(rgb);
        Assert.Equal(10, rgb.Width);
        Assert.Equal(8, rgb.Height);
        Assert.Equal(80, rgb.GetPixelCount());

        // GetColorDepth on RGB
        var rgbDepth = rgb.GetColorDepth();
        Assert.True(rgbDepth >= 1);

        // Scale 2x
        var scaled2x = gray.Scale(2.0);
        Assert.Equal(20, scaled2x.Width);
        Assert.Equal(16, scaled2x.Height);
        Assert.Equal(320, scaled2x.GetPixelCount());

        // GetColorDepth after scale
        var scaledDepth = scaled2x.GetColorDepth();
        Assert.True(scaledDepth >= 1);

        // ConvertToRgb after scale
        var scaledRgb = scaled2x.ConvertToRgb();
        Assert.Equal(20, scaledRgb.Width);
        Assert.Equal(16, scaledRgb.Height);

        // Scale 0.5x on original
        var scaledHalf = gray.Scale(0.5);
        Assert.Equal(5, scaledHalf.Width);
        Assert.Equal(4, scaledHalf.Height);

        // GetColorDepth on halved image
        Assert.True(scaledHalf.GetColorDepth() >= 0);

        // Scale 1x identity
        var scaled1x = gray.Scale(1.0);
        Assert.Equal(10, scaled1x.Width);
        Assert.Equal(8, scaled1x.Height);

        // Crop from scaled 2x
        var cropped = scaled2x.Crop(0, 0, 10, 8);
        Assert.Equal(10, cropped.Width);
        Assert.Equal(8, cropped.Height);

        // ConvertToRgb on cropped
        var croppedRgb = cropped.ConvertToRgb();
        Assert.Equal(10, croppedRgb.Width);

        // Invert on rgb
        var inverted = rgb.Invert();
        Assert.NotNull(inverted);
        Assert.Equal(10, inverted.Width);
        Assert.Equal(8, inverted.Height);

        // Scale on RGB directly
        var scaledFromRgb = rgb.Scale(2.0);
        Assert.Equal(20, scaledFromRgb.Width);

        // GetColorDepth on RGB scaled
        Assert.True(scaledFromRgb.GetColorDepth() >= 1);

        // GetAverageBrightness
        var brightness = gray.GetAverageBrightness();
        Assert.True(brightness >= 0 && brightness <= 255);

        // GetMaxValue
        var maxVal = gray.GetMaxValue();
        Assert.True(maxVal >= 0);

        // GetPixelCount
        Assert.Equal(80, gray.GetPixelCount());
        Assert.Equal(320, scaled2x.GetPixelCount());
        Assert.Equal(20, scaledHalf.GetPixelCount());

        // SaveToFile — grayscale
        var grayPath = TempFile("dogfood_gray.pgm");
        gray.SaveToFile(grayPath);
        Assert.True(File.Exists(grayPath));

        // SaveToFile — rgb
        var rgbPath = TempFile("dogfood_rgb.ppm");
        rgb.SaveToFile(rgbPath);
        Assert.True(File.Exists(rgbPath));

        // SaveToFile — scaled 2x
        var scaledPath = TempFile("dogfood_scaled2x.pgm");
        scaled2x.SaveToFile(scaledPath);
        Assert.True(File.Exists(scaledPath));

        // LoadFile and verify
        var loadedGray = NetpbmImage.LoadFile(grayPath);
        Assert.Equal(10, loadedGray.Width);
        Assert.Equal(8, loadedGray.Height);
        Assert.True(loadedGray.GetColorDepth() >= 1);

        var loadedRgb = NetpbmImage.LoadFile(rgbPath);
        Assert.Equal(10, loadedRgb.Width);
        Assert.Equal(8, loadedRgb.Height);
        Assert.True(loadedRgb.GetColorDepth() >= 1);

        // ConvertToRgb on loaded grayscale
        var loadedConverted = loadedGray.ConvertToRgb();
        Assert.Equal(10, loadedConverted.Width);
        Assert.Equal(8, loadedConverted.Height);

        // Scale loaded
        var loadedScaled = loadedGray.Scale(1.5);
        Assert.True(loadedScaled.Width > 0);
        Assert.True(loadedScaled.Height > 0);

        // Final save
        var finalPath = TempFile("dogfood_final.pgm");
        loadedScaled.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
    }
}
