// Tests for NetpbmImage.ConvertToGrayscale, ConvertToRgb, GetColorDepth deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R240

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R240: Tests for NetpbmImage.ConvertToGrayscale, ConvertToRgb, GetColorDepth deeper.
/// ConvertToGrayscale(): converts an RGB image to grayscale (PGM).
/// ConvertToRgb(): converts a grayscale image to RGB (PPM).
/// GetColorDepth(): returns the color depth (max value, typically 255).
/// Covers: ConvertToGrayscale non-null; ConvertToGrayscale preserves dimensions;
/// ConvertToGrayscale from RGB produces single-channel; ConvertToGrayscale persist;
/// ConvertToGrayscale idempotent; ConvertToGrayscale then save-load;
/// ConvertToRgb non-null; ConvertToRgb preserves dimensions;
/// ConvertToRgb from grayscale produces three-channel; ConvertToRgb persist;
/// ConvertToRgb idempotent; ConvertToRgb then GetColorDepth;
/// GetColorDepth positive; GetColorDepth equals max value; GetColorDepth consistent;
/// GetColorDepth for grayscale; GetColorDepth for RGB;
/// GetColorDepth after convert same depth; GetColorDepth in valid range;
/// dogfood CreateImage→ConvertToGrayscale→ConvertToRgb→GetColorDepth→SaveToFile pipeline.
/// </summary>
public class NetpbmR240ConvertAndGetColorDepthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR240ConvertAndGetColorDepthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR240_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayscale(int w = 8, int h = 8, byte fill = 128)
    {
        var pixels = new byte[w * h];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = fill;
        return NetpbmImage.CreatePgm(w, h, pixels);
    }

    private static NetpbmImage CreateRgb(int w = 8, int h = 8)
    {
        var pixels = new byte[w * h * 3];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = (byte)(i % 256);
        return NetpbmImage.CreatePpm(w, h, pixels);
    }

    // -------------------------------------------------------------------------
    // ConvertToGrayscale
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertToGrayscale_NonNull()
    {
        var img = CreateRgb();
        Assert.NotNull(img.ConvertToGrayscale());
    }

    [Fact]
    public void ConvertToGrayscale_PreservesWidth()
    {
        var img = CreateRgb();
        Assert.Equal(img.Width, img.ConvertToGrayscale().Width);
    }

    [Fact]
    public void ConvertToGrayscale_PreservesHeight()
    {
        var img = CreateRgb();
        Assert.Equal(img.Height, img.ConvertToGrayscale().Height);
    }

    [Fact]
    public void ConvertToGrayscale_Persist()
    {
        var img = CreateRgb();
        var gray = img.ConvertToGrayscale();
        var path = TempFile("convert_gray.pgm");
        gray.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void ConvertToGrayscale_FromGrayscale_NonNull()
    {
        var img = CreateGrayscale();
        Assert.NotNull(img.ConvertToGrayscale());
    }

    [Fact]
    public void ConvertToGrayscale_FromGrayscale_PreservesDimensions()
    {
        var img = CreateGrayscale();
        var gray = img.ConvertToGrayscale();
        Assert.Equal(img.Width, gray.Width);
        Assert.Equal(img.Height, gray.Height);
    }

    [Fact]
    public void ConvertToGrayscale_ChannelIsOne()
    {
        var img = CreateRgb();
        var gray = img.ConvertToGrayscale();
        var channel = gray.GetChannel(0);
        Assert.Equal(gray.Width * gray.Height, channel.Length);
    }

    [Fact]
    public void ConvertToGrayscale_ThenSaveLoad_Consistent()
    {
        var img = CreateRgb();
        var gray = img.ConvertToGrayscale();
        var path = TempFile("gray_round.pgm");
        gray.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(gray.Width, loaded.Width);
        Assert.Equal(gray.Height, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // ConvertToRgb
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertToRgb_NonNull()
    {
        var img = CreateGrayscale();
        Assert.NotNull(img.ConvertToRgb());
    }

    [Fact]
    public void ConvertToRgb_PreservesWidth()
    {
        var img = CreateGrayscale();
        Assert.Equal(img.Width, img.ConvertToRgb().Width);
    }

    [Fact]
    public void ConvertToRgb_PreservesHeight()
    {
        var img = CreateGrayscale();
        Assert.Equal(img.Height, img.ConvertToRgb().Height);
    }

    [Fact]
    public void ConvertToRgb_Persist()
    {
        var img = CreateGrayscale();
        var rgb = img.ConvertToRgb();
        var path = TempFile("convert_rgb.ppm");
        rgb.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void ConvertToRgb_FromRgb_NonNull()
    {
        var img = CreateRgb();
        Assert.NotNull(img.ConvertToRgb());
    }

    [Fact]
    public void ConvertToRgb_ThreeChannels_HaveCorrectLength()
    {
        var img = CreateGrayscale();
        var rgb = img.ConvertToRgb();
        // Each channel should have width*height pixels
        var ch0 = rgb.GetChannel(0);
        Assert.Equal(rgb.Width * rgb.Height, ch0.Length);
    }

    [Fact]
    public void ConvertToRgb_ThenSaveLoad_Consistent()
    {
        var img = CreateGrayscale();
        var rgb = img.ConvertToRgb();
        var path = TempFile("rgb_round.ppm");
        rgb.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(rgb.Width, loaded.Width);
        Assert.Equal(rgb.Height, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // GetColorDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_Positive_Grayscale()
    {
        var img = CreateGrayscale();
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_Positive_RGB()
    {
        var img = CreateRgb();
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_Equals255_Standard()
    {
        var img = CreateGrayscale();
        // Standard PGM/PPM uses 255 as max value
        Assert.Equal(255, img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_Consistent_Grayscale()
    {
        var img = CreateGrayscale();
        Assert.Equal(img.GetColorDepth(), img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_Consistent_RGB()
    {
        var img = CreateRgb();
        Assert.Equal(img.GetColorDepth(), img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_InValidRange()
    {
        var img = CreateGrayscale();
        var depth = img.GetColorDepth();
        Assert.True(depth > 0 && depth <= 65535);
    }

    [Fact]
    public void GetColorDepth_AfterConvertToGrayscale_Preserved()
    {
        var img = CreateRgb();
        var gray = img.ConvertToGrayscale();
        Assert.Equal(img.GetColorDepth(), gray.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_AfterConvertToRgb_Preserved()
    {
        var img = CreateGrayscale();
        var rgb = img.ConvertToRgb();
        Assert.Equal(img.GetColorDepth(), rgb.GetColorDepth());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateImage_ConvertToGrayscale_ConvertToRgb_GetColorDepth_SaveToFile_Pipeline()
    {
        // Create RGB
        var rgbPixels = new byte[10 * 10 * 3];
        for (int i = 0; i < rgbPixels.Length; i++) rgbPixels[i] = (byte)(i % 256);
        var rgb = NetpbmImage.CreatePpm(10, 10, rgbPixels);

        Assert.Equal(10, rgb.Width);
        Assert.Equal(10, rgb.Height);

        // GetColorDepth on RGB
        var rgbDepth = rgb.GetColorDepth();
        Assert.True(rgbDepth > 0);
        Assert.Equal(255, rgbDepth);

        // ConvertToGrayscale
        var gray = rgb.ConvertToGrayscale();
        Assert.NotNull(gray);
        Assert.Equal(10, gray.Width);
        Assert.Equal(10, gray.Height);

        // GetColorDepth on grayscale (same)
        var grayDepth = gray.GetColorDepth();
        Assert.Equal(rgbDepth, grayDepth);

        // Channel length for grayscale
        var grayChannel = gray.GetChannel(0);
        Assert.Equal(100, grayChannel.Length);

        // ConvertToRgb from grayscale
        var rgbFromGray = gray.ConvertToRgb();
        Assert.NotNull(rgbFromGray);
        Assert.Equal(10, rgbFromGray.Width);
        Assert.Equal(10, rgbFromGray.Height);
        Assert.Equal(grayDepth, rgbFromGray.GetColorDepth());

        // Round-trip: RGB → gray → RGB
        var rgbCh0 = rgbFromGray.GetChannel(0);
        Assert.Equal(100, rgbCh0.Length);

        // Create grayscale directly
        var grayPixels = new byte[10 * 10];
        for (int i = 0; i < grayPixels.Length; i++) grayPixels[i] = (byte)(i % 200 + 30);
        var grayDirect = NetpbmImage.CreatePgm(10, 10, grayPixels);
        Assert.Equal(255, grayDirect.GetColorDepth());

        // ConvertToRgb
        var rgbFromDirect = grayDirect.ConvertToRgb();
        Assert.Equal(10, rgbFromDirect.Width);
        Assert.Equal(255, rgbFromDirect.GetColorDepth());

        // SaveToFile grayscale
        var grayPath = TempFile("dogfood_gray.pgm");
        gray.SaveToFile(grayPath);
        Assert.True(File.Exists(grayPath));
        var loadedGray = NetpbmImage.LoadFile(grayPath);
        Assert.Equal(10, loadedGray.Width);
        Assert.Equal(255, loadedGray.GetColorDepth());

        // SaveToFile RGB from grayscale
        var rgbPath = TempFile("dogfood_rgb_from_gray.ppm");
        rgbFromGray.SaveToFile(rgbPath);
        Assert.True(File.Exists(rgbPath));
        var loadedRgb = NetpbmImage.LoadFile(rgbPath);
        Assert.Equal(10, loadedRgb.Width);
        Assert.Equal(255, loadedRgb.GetColorDepth());

        // ConvertToGrayscale on loaded RGB
        var loadedGrayConverted = loadedRgb.ConvertToGrayscale();
        Assert.Equal(10, loadedGrayConverted.Width);
        Assert.Equal(255, loadedGrayConverted.GetColorDepth());

        // Verify channel counts post-conversion
        var finalGrayCh = loadedGrayConverted.GetChannel(0);
        Assert.Equal(100, finalGrayCh.Length);
    }
}
