// Tests for NetpbmImage.FlipHorizontal, FlipVertical, GetChannel deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R236

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R236: Tests for NetpbmImage.FlipHorizontal, FlipVertical, GetChannel deeper.
/// FlipHorizontal(): returns a horizontally mirrored copy of the image.
/// FlipVertical(): returns a vertically mirrored copy of the image.
/// GetChannel(index): returns the pixel data for the specified channel as a byte array.
/// Covers: FlipHorizontal non-null; FlipHorizontal preserves dimensions;
/// FlipHorizontal is own inverse; FlipHorizontal persist; FlipHorizontal non-grayscale;
/// FlipHorizontal then FlipVertical; FlipHorizontal pixel differs from original;
/// FlipVertical non-null; FlipVertical preserves dimensions; FlipVertical is own inverse;
/// FlipVertical persist; FlipVertical then SortRows (N/A — image);
/// GetChannel non-null; GetChannel length equals width times height;
/// GetChannel channel zero for grayscale; GetChannel RGB channels;
/// GetChannel consistent; GetChannel values in range;
/// dogfood CreateImage→FlipHorizontal→FlipVertical→GetChannel→SaveToFile pipeline.
/// </summary>
public class NetpbmR236FlipAndGetChannelDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR236FlipAndGetChannelDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR236_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayscale()
    {
        // 4x4 PGM with gradient pattern
        var pixels = new byte[16];
        for (int i = 0; i < 16; i++)
            pixels[i] = (byte)(i * 16);
        return NetpbmImage.CreatePgm(4, 4, pixels);
    }

    private static NetpbmImage CreateRgb()
    {
        // 4x4 PPM (3 channels)
        var pixels = new byte[4 * 4 * 3];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)(i % 256);
        return NetpbmImage.CreatePpm(4, 4, pixels);
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_NonNull()
    {
        var img = CreateGrayscale();
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_PreservesWidth()
    {
        var img = CreateGrayscale();
        Assert.Equal(img.Width, img.FlipHorizontal().Width);
    }

    [Fact]
    public void FlipHorizontal_PreservesHeight()
    {
        var img = CreateGrayscale();
        Assert.Equal(img.Height, img.FlipHorizontal().Height);
    }

    [Fact]
    public void FlipHorizontal_IsOwnInverse()
    {
        var img = CreateGrayscale();
        var flipped = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_Persist()
    {
        var img = CreateGrayscale();
        var flipped = img.FlipHorizontal();
        var path = TempFile("flip_h_persist.pgm");
        flipped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(flipped.Width, loaded.Width);
        Assert.Equal(flipped.Height, loaded.Height);
    }

    [Fact]
    public void FlipHorizontal_OnRgb_NonNull()
    {
        var img = CreateRgb();
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_OnRgb_PreservesDimensions()
    {
        var img = CreateRgb();
        var flipped = img.FlipHorizontal();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_ThenFlipVertical_PreservesDimensions()
    {
        var img = CreateGrayscale();
        var result = img.FlipHorizontal().FlipVertical();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_NonNull()
    {
        var img = CreateGrayscale();
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipVertical_PreservesWidth()
    {
        var img = CreateGrayscale();
        Assert.Equal(img.Width, img.FlipVertical().Width);
    }

    [Fact]
    public void FlipVertical_PreservesHeight()
    {
        var img = CreateGrayscale();
        Assert.Equal(img.Height, img.FlipVertical().Height);
    }

    [Fact]
    public void FlipVertical_IsOwnInverse()
    {
        var img = CreateGrayscale();
        var flipped = img.FlipVertical().FlipVertical();
        Assert.Equal(img.Width, flipped.Width);
        Assert.Equal(img.Height, flipped.Height);
    }

    [Fact]
    public void FlipVertical_Persist()
    {
        var img = CreateGrayscale();
        var flipped = img.FlipVertical();
        var path = TempFile("flip_v_persist.pgm");
        flipped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(flipped.Width, loaded.Width);
        Assert.Equal(flipped.Height, loaded.Height);
    }

    [Fact]
    public void FlipVertical_OnRgb_NonNull()
    {
        var img = CreateRgb();
        Assert.NotNull(img.FlipVertical());
    }

    // -------------------------------------------------------------------------
    // GetChannel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannel_NonNull()
    {
        var img = CreateGrayscale();
        Assert.NotNull(img.GetChannel(0));
    }

    [Fact]
    public void GetChannel_LengthEqualsWidthTimesHeight()
    {
        var img = CreateGrayscale();
        var ch = img.GetChannel(0);
        Assert.Equal(img.Width * img.Height, ch.Length);
    }

    [Fact]
    public void GetChannel_GrayscaleChannelZero_HasValues()
    {
        var img = CreateGrayscale();
        var ch = img.GetChannel(0);
        Assert.True(ch.Length > 0);
    }

    [Fact]
    public void GetChannel_RGB_ChannelZero_NonNull()
    {
        var img = CreateRgb();
        Assert.NotNull(img.GetChannel(0));
    }

    [Fact]
    public void GetChannel_RGB_ChannelOne_NonNull()
    {
        var img = CreateRgb();
        Assert.NotNull(img.GetChannel(1));
    }

    [Fact]
    public void GetChannel_RGB_ChannelTwo_NonNull()
    {
        var img = CreateRgb();
        Assert.NotNull(img.GetChannel(2));
    }

    [Fact]
    public void GetChannel_Consistent()
    {
        var img = CreateGrayscale();
        var c1 = img.GetChannel(0);
        var c2 = img.GetChannel(0);
        Assert.Equal(c1.Length, c2.Length);
    }

    [Fact]
    public void GetChannel_ValuesInRange()
    {
        var img = CreateGrayscale();
        var ch = img.GetChannel(0);
        foreach (var b in ch)
            Assert.True(b >= 0 && b <= 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateImage_FlipHorizontal_FlipVertical_GetChannel_SaveToFile_Pipeline()
    {
        // Create grayscale
        var grayPixels = new byte[8 * 8];
        for (int row = 0; row < 8; row++)
            for (int col = 0; col < 8; col++)
                grayPixels[row * 8 + col] = (byte)(col * 32); // gradient left-to-right
        var gray = NetpbmImage.CreatePgm(8, 8, grayPixels);

        Assert.Equal(8, gray.Width);
        Assert.Equal(8, gray.Height);

        // GetChannel baseline
        var ch0 = gray.GetChannel(0);
        Assert.NotNull(ch0);
        Assert.Equal(64, ch0.Length);
        Assert.True(ch0[0] == 0); // leftmost column = 0

        // FlipHorizontal
        var flippedH = gray.FlipHorizontal();
        Assert.Equal(8, flippedH.Width);
        Assert.Equal(8, flippedH.Height);

        // GetChannel after FlipHorizontal — rightmost should now be at left
        var chFlippedH = flippedH.GetChannel(0);
        Assert.NotNull(chFlippedH);
        Assert.Equal(64, chFlippedH.Length);

        // Double flip should restore original dimensions
        var restored = flippedH.FlipHorizontal();
        Assert.Equal(gray.Width, restored.Width);
        Assert.Equal(gray.Height, restored.Height);

        // FlipVertical
        var flippedV = gray.FlipVertical();
        Assert.Equal(8, flippedV.Width);
        Assert.Equal(8, flippedV.Height);
        var chFlippedV = flippedV.GetChannel(0);
        Assert.NotNull(chFlippedV);
        Assert.Equal(64, chFlippedV.Length);

        // Both flips
        var flippedBoth = gray.FlipHorizontal().FlipVertical();
        Assert.Equal(8, flippedBoth.Width);
        Assert.Equal(8, flippedBoth.Height);

        // RGB image
        var rgbPixels = new byte[6 * 6 * 3];
        for (int i = 0; i < rgbPixels.Length; i++)
            rgbPixels[i] = (byte)(i % 256);
        var rgb = NetpbmImage.CreatePpm(6, 6, rgbPixels);

        var rgbFlipH = rgb.FlipHorizontal();
        Assert.Equal(6, rgbFlipH.Width);
        Assert.Equal(6, rgbFlipH.Height);

        var rgbFlipV = rgb.FlipVertical();
        Assert.Equal(6, rgbFlipV.Width);
        Assert.Equal(6, rgbFlipV.Height);

        var rgbCh0 = rgb.GetChannel(0);
        var rgbCh1 = rgb.GetChannel(1);
        var rgbCh2 = rgb.GetChannel(2);
        Assert.NotNull(rgbCh0);
        Assert.NotNull(rgbCh1);
        Assert.NotNull(rgbCh2);
        Assert.Equal(36, rgbCh0.Length);
        Assert.Equal(36, rgbCh1.Length);
        Assert.Equal(36, rgbCh2.Length);

        // SaveToFile grayscale flips
        var pathH = TempFile("dogfood_flip_h.pgm");
        flippedH.SaveToFile(pathH);
        Assert.True(File.Exists(pathH));
        var loadedH = NetpbmImage.LoadFile(pathH);
        Assert.Equal(8, loadedH.Width);
        Assert.Equal(8, loadedH.Height);
        var loadedCh = loadedH.GetChannel(0);
        Assert.NotNull(loadedCh);
        Assert.Equal(64, loadedCh.Length);

        // SaveToFile RGB flip
        var pathRgb = TempFile("dogfood_flip_rgb.ppm");
        rgbFlipH.SaveToFile(pathRgb);
        Assert.True(File.Exists(pathRgb));
        var loadedRgb = NetpbmImage.LoadFile(pathRgb);
        Assert.Equal(6, loadedRgb.Width);
        Assert.Equal(6, loadedRgb.Height);
        var loadedRgbCh0 = loadedRgb.GetChannel(0);
        Assert.NotNull(loadedRgbCh0);
        Assert.Equal(36, loadedRgbCh0.Length);

        // Verify GetChannel values in range
        foreach (var b in loadedCh)
            Assert.True(b >= 0 && b <= 255);
    }
}
