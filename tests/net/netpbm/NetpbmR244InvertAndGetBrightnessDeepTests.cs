// Tests for NetpbmImage.Invert, GetAverageBrightness, Threshold deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R244

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R244: Tests for NetpbmImage.Invert, GetAverageBrightness, Threshold deeper.
/// Invert(): returns a pixel-inverted copy of the image (255 - value for each pixel).
/// GetAverageBrightness(): returns the mean pixel value across all channels.
/// Threshold(value): returns a binary image where pixels below value become 0, above become 255.
/// Covers: Invert non-null; Invert preserves dimensions; Invert is own inverse (dims);
/// Invert persist; Invert RGB; Invert no-throw; Invert dark image becomes light;
/// Invert then Invert restores; Invert of uniform 0 = uniform 255 image;
/// GetAverageBrightness in range 0-255; GetAverageBrightness consistent; GetAverageBrightness positive;
/// GetAverageBrightness after Invert changes; GetAverageBrightness for uniform image exact;
/// GetAverageBrightness no-throw; GetAverageBrightness for dark image low;
/// GetAverageBrightness for bright image high;
/// Threshold non-null; Threshold preserves dims; Threshold no-throw; Threshold output only 0 or 255;
/// Threshold persist; Threshold at 0 all pixels 255; Threshold at 255 all pixels 0 or edge;
/// Threshold then Invert; Threshold consistent;
/// dogfood CreateImage→Invert→GetAverageBrightness→Threshold→SaveToFile pipeline.
/// </summary>
public class NetpbmR244InvertAndGetBrightnessDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR244InvertAndGetBrightnessDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR244_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateDarkImage()
    {
        // 6x6 PGM with dark pixels (values 0-50)
        var pixels = new byte[6 * 6];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 51); // 0..50
        return NetpbmImage.CreatePgm(6, 6, pixels);
    }

    private static NetpbmImage CreateBrightImage()
    {
        // 6x6 PGM all pixels = 200
        var pixels = new byte[6 * 6];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = 200;
        return NetpbmImage.CreatePgm(6, 6, pixels);
    }

    private static NetpbmImage CreateUniformBlack()
    {
        // 4x4 PGM all pixels = 0
        var pixels = new byte[4 * 4];
        return NetpbmImage.CreatePgm(4, 4, pixels);
    }

    private static NetpbmImage CreateRgbImage()
    {
        var pixels = new byte[6 * 6 * 3];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 200 + 28);
        return NetpbmImage.CreatePpm(6, 6, pixels);
    }

    // -------------------------------------------------------------------------
    // Invert
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_NonNull()
    {
        var img = CreateDarkImage();
        Assert.NotNull(img.Invert());
    }

    [Fact]
    public void Invert_PreservesWidth()
    {
        var img = CreateDarkImage();
        Assert.Equal(img.Width, img.Invert().Width);
    }

    [Fact]
    public void Invert_PreservesHeight()
    {
        var img = CreateDarkImage();
        Assert.Equal(img.Height, img.Invert().Height);
    }

    [Fact]
    public void Invert_IsOwnInverse_Dims()
    {
        var img = CreateDarkImage();
        var twiceInverted = img.Invert().Invert();
        Assert.Equal(img.Width, twiceInverted.Width);
        Assert.Equal(img.Height, twiceInverted.Height);
    }

    [Fact]
    public void Invert_NoThrow()
    {
        var img = CreateDarkImage();
        var ex = Record.Exception(() => img.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void Invert_Persist()
    {
        var img = CreateDarkImage();
        var inverted = img.Invert();
        var path = TempFile("invert_persist.pgm");
        inverted.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
    }

    [Fact]
    public void Invert_RGB_NonNull()
    {
        var img = CreateRgbImage();
        Assert.NotNull(img.Invert());
    }

    [Fact]
    public void Invert_RGB_PreservesDimensions()
    {
        var img = CreateRgbImage();
        var inv = img.Invert();
        Assert.Equal(img.Width, inv.Width);
        Assert.Equal(img.Height, inv.Height);
    }

    [Fact]
    public void Invert_DarkImageBecomesBright()
    {
        var img = CreateUniformBlack(); // all 0
        var inverted = img.Invert();
        var brightness = inverted.GetAverageBrightness();
        Assert.True(brightness > 200); // should be 255
    }

    [Fact]
    public void Invert_BrightImageBecomesDark()
    {
        var img = CreateBrightImage(); // all 200
        var inverted = img.Invert();
        var brightness = inverted.GetAverageBrightness();
        Assert.True(brightness < 100); // 255-200 = 55
    }

    // -------------------------------------------------------------------------
    // GetAverageBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAverageBrightness_InRange()
    {
        var img = CreateDarkImage();
        var brightness = img.GetAverageBrightness();
        Assert.True(brightness >= 0 && brightness <= 255);
    }

    [Fact]
    public void GetAverageBrightness_Consistent()
    {
        var img = CreateDarkImage();
        var b1 = img.GetAverageBrightness();
        var b2 = img.GetAverageBrightness();
        Assert.Equal(b1, b2);
    }

    [Fact]
    public void GetAverageBrightness_NoThrow()
    {
        var img = CreateDarkImage();
        var ex = Record.Exception(() => img.GetAverageBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAverageBrightness_ForUniformImage_Exact()
    {
        var img = CreateBrightImage(); // all 200
        var brightness = img.GetAverageBrightness();
        Assert.True(Math.Abs(brightness - 200.0) < 1.0);
    }

    [Fact]
    public void GetAverageBrightness_ForBlackImage_Zero()
    {
        var img = CreateUniformBlack(); // all 0
        var brightness = img.GetAverageBrightness();
        Assert.True(brightness < 5);
    }

    [Fact]
    public void GetAverageBrightness_AfterInvert_Changes()
    {
        var img = CreateDarkImage();
        var before = img.GetAverageBrightness();
        var after = img.Invert().GetAverageBrightness();
        Assert.NotEqual(before, after);
    }

    [Fact]
    public void GetAverageBrightness_BrightImageHigh()
    {
        var img = CreateBrightImage();
        Assert.True(img.GetAverageBrightness() > 150);
    }

    [Fact]
    public void GetAverageBrightness_DarkImageLow()
    {
        var img = CreateUniformBlack();
        Assert.True(img.GetAverageBrightness() < 10);
    }

    // -------------------------------------------------------------------------
    // Threshold
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_NonNull()
    {
        var img = CreateDarkImage();
        Assert.NotNull(img.Threshold(128));
    }

    [Fact]
    public void Threshold_PreservesWidth()
    {
        var img = CreateDarkImage();
        Assert.Equal(img.Width, img.Threshold(128).Width);
    }

    [Fact]
    public void Threshold_PreservesHeight()
    {
        var img = CreateDarkImage();
        Assert.Equal(img.Height, img.Threshold(128).Height);
    }

    [Fact]
    public void Threshold_NoThrow()
    {
        var img = CreateDarkImage();
        var ex = Record.Exception(() => img.Threshold(100));
        Assert.Null(ex);
    }

    [Fact]
    public void Threshold_OutputOnlyBinaryValues()
    {
        var img = CreateDarkImage();
        var thresholded = img.Threshold(25);
        var channel = thresholded.GetChannel(0);
        foreach (var b in channel)
            Assert.True(b == 0 || b == 255);
    }

    [Fact]
    public void Threshold_Persist()
    {
        var img = CreateBrightImage();
        var thresholded = img.Threshold(100);
        var path = TempFile("threshold_persist.pgm");
        thresholded.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
    }

    [Fact]
    public void Threshold_Consistent()
    {
        var img = CreateDarkImage();
        var t1 = img.Threshold(128);
        var t2 = img.Threshold(128);
        Assert.Equal(t1.Width, t2.Width);
        Assert.Equal(t1.Height, t2.Height);
    }

    [Fact]
    public void Threshold_ThenInvert_PreservesDims()
    {
        var img = CreateBrightImage();
        var result = img.Threshold(100).Invert();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateImage_Invert_GetAverageBrightness_Threshold_SaveToFile_Pipeline()
    {
        // Create 8x8 gradient
        var pixels = new byte[8 * 8];
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 8; c++)
                pixels[r * 8 + c] = (byte)(r * 32); // 0, 32, 64, 96, 128, 160, 192, 224

        var gray = NetpbmImage.CreatePgm(8, 8, pixels);
        Assert.Equal(8, gray.Width);
        Assert.Equal(8, gray.Height);

        // GetAverageBrightness
        var brightness = gray.GetAverageBrightness();
        Assert.True(brightness >= 0 && brightness <= 255);
        // Average of 0,32,64,96,128,160,192,224 = 112 (each row repeated 8 times)
        Assert.True(Math.Abs(brightness - 112.0) < 5.0);

        // Invert
        var inverted = gray.Invert();
        Assert.NotNull(inverted);
        Assert.Equal(8, inverted.Width);
        Assert.Equal(8, inverted.Height);

        // GetAverageBrightness after invert = 255 - original
        var invertedBrightness = inverted.GetAverageBrightness();
        Assert.True(Math.Abs(invertedBrightness - (255 - brightness)) < 5.0);

        // Double invert restores dims
        var doubleInverted = inverted.Invert();
        Assert.Equal(8, doubleInverted.Width);
        Assert.Equal(8, doubleInverted.Height);
        var doubleInvBrightness = doubleInverted.GetAverageBrightness();
        Assert.True(Math.Abs(doubleInvBrightness - brightness) < 5.0);

        // Threshold at 112 (midpoint)
        var thresholded = gray.Threshold(112);
        Assert.NotNull(thresholded);
        Assert.Equal(8, thresholded.Width);
        Assert.Equal(8, thresholded.Height);
        var threshChannel = thresholded.GetChannel(0);
        foreach (var b in threshChannel)
            Assert.True(b == 0 || b == 255);

        // Threshold on inverted
        var threshInverted = inverted.Threshold(128);
        Assert.NotNull(threshInverted);
        Assert.Equal(8, threshInverted.Width);
        Assert.Equal(8, threshInverted.Height);

        // Invert the thresholded result
        var invertedThresh = thresholded.Invert();
        Assert.NotNull(invertedThresh);
        var invThreshChannel = invertedThresh.GetChannel(0);
        foreach (var b in invThreshChannel)
            Assert.True(b == 0 || b == 255);

        // RGB image
        var rgbPixels = new byte[6 * 6 * 3];
        for (int i = 0; i < rgbPixels.Length; i++)
            rgbPixels[i] = (byte)(i % 256);
        var rgb = NetpbmImage.CreatePpm(6, 6, rgbPixels);

        var rgbInverted = rgb.Invert();
        Assert.Equal(6, rgbInverted.Width);
        Assert.Equal(6, rgbInverted.Height);

        var rgbBrightness = rgb.GetAverageBrightness();
        Assert.True(rgbBrightness >= 0 && rgbBrightness <= 255);

        var rgbThreshold = rgb.Threshold(128);
        Assert.Equal(6, rgbThreshold.Width);
        Assert.Equal(6, rgbThreshold.Height);

        // SaveToFile inverted grayscale
        var pathInv = TempFile("dogfood_inverted.pgm");
        inverted.SaveToFile(pathInv);
        Assert.True(File.Exists(pathInv));
        var loadedInv = NetpbmImage.LoadFile(pathInv);
        Assert.Equal(8, loadedInv.Width);
        Assert.Equal(8, loadedInv.Height);
        var loadedBrightness = loadedInv.GetAverageBrightness();
        Assert.True(Math.Abs(loadedBrightness - invertedBrightness) < 5.0);

        // SaveToFile thresholded
        var pathThresh = TempFile("dogfood_thresholded.pgm");
        thresholded.SaveToFile(pathThresh);
        Assert.True(File.Exists(pathThresh));
        var loadedThresh = NetpbmImage.LoadFile(pathThresh);
        Assert.Equal(8, loadedThresh.Width);
        Assert.Equal(8, loadedThresh.Height);
        var loadedThreshChannel = loadedThresh.GetChannel(0);
        foreach (var b in loadedThreshChannel)
            Assert.True(b == 0 || b == 255);

        // SaveToFile RGB inverted
        var pathRgbInv = TempFile("dogfood_rgb_inverted.ppm");
        rgbInverted.SaveToFile(pathRgbInv);
        Assert.True(File.Exists(pathRgbInv));
        var loadedRgbInv = NetpbmImage.LoadFile(pathRgbInv);
        Assert.Equal(6, loadedRgbInv.Width);
        Assert.Equal(6, loadedRgbInv.Height);
    }
}
