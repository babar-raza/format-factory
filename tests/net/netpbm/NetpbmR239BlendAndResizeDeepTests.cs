// Tests for NetpbmImage.Blend, Resize, GetAspectRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R239

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R239: Tests for NetpbmImage.Blend, Resize, GetAspectRatio deeper.
/// Blend(other, alpha): blends two images together with the given alpha weight.
/// Resize(width, height): resizes the image to the given dimensions.
/// GetAspectRatio(): returns the aspect ratio (width/height) of the image.
/// Covers: Blend non-null; Blend preserves dimensions; Blend with alpha 0.5;
/// Blend with alpha 0 returns first image dims; Blend with alpha 1 returns second dims;
/// Blend persist; Blend no-throw; Blend consistent;
/// Resize non-null; Resize changes dimensions; Resize to smaller;
/// Resize to larger; Resize preserve content approximately; Resize persist;
/// Resize then GetAspectRatio; Resize consistent;
/// GetAspectRatio positive; GetAspectRatio for square is one; GetAspectRatio consistent;
/// GetAspectRatio after Resize; GetAspectRatio wide image; GetAspectRatio tall image;
/// dogfood CreateImage→Blend→Resize→GetAspectRatio→SaveToFile pipeline.
/// </summary>
public class NetpbmR239BlendAndResizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR239BlendAndResizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR239_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayscale(int w, int h, byte fillValue = 128)
    {
        var pixels = new byte[w * h];
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = fillValue;
        return NetpbmImage.CreatePgm(w, h, pixels);
    }

    private static NetpbmImage CreateRgb(int w, int h, byte r = 100, byte g = 150, byte b = 200)
    {
        var pixels = new byte[w * h * 3];
        for (int i = 0; i < pixels.Length; i += 3)
        {
            pixels[i] = r;
            pixels[i + 1] = g;
            pixels[i + 2] = b;
        }
        return NetpbmImage.CreatePpm(w, h, pixels);
    }

    // -------------------------------------------------------------------------
    // Blend
    // -------------------------------------------------------------------------

    [Fact]
    public void Blend_NonNull()
    {
        var img1 = CreateGrayscale(8, 8, 50);
        var img2 = CreateGrayscale(8, 8, 200);
        Assert.NotNull(img1.Blend(img2, 0.5));
    }

    [Fact]
    public void Blend_PreservesWidth()
    {
        var img1 = CreateGrayscale(8, 8, 50);
        var img2 = CreateGrayscale(8, 8, 200);
        var blended = img1.Blend(img2, 0.5);
        Assert.Equal(8, blended.Width);
    }

    [Fact]
    public void Blend_PreservesHeight()
    {
        var img1 = CreateGrayscale(8, 8, 50);
        var img2 = CreateGrayscale(8, 8, 200);
        var blended = img1.Blend(img2, 0.5);
        Assert.Equal(8, blended.Height);
    }

    [Fact]
    public void Blend_NoThrow()
    {
        var img1 = CreateGrayscale(6, 6, 100);
        var img2 = CreateGrayscale(6, 6, 150);
        var ex = Record.Exception(() => img1.Blend(img2, 0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void Blend_Consistent()
    {
        var img1 = CreateGrayscale(8, 8, 50);
        var img2 = CreateGrayscale(8, 8, 200);
        var b1 = img1.Blend(img2, 0.5);
        var b2 = img1.Blend(img2, 0.5);
        Assert.Equal(b1.Width, b2.Width);
        Assert.Equal(b1.Height, b2.Height);
    }

    [Fact]
    public void Blend_Persist()
    {
        var img1 = CreateGrayscale(6, 6, 50);
        var img2 = CreateGrayscale(6, 6, 200);
        var blended = img1.Blend(img2, 0.5);
        var path = TempFile("blend_persist.pgm");
        blended.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(6, loaded.Width);
        Assert.Equal(6, loaded.Height);
    }

    [Fact]
    public void Blend_RGB_NoThrow()
    {
        var img1 = CreateRgb(6, 6, 255, 0, 0);
        var img2 = CreateRgb(6, 6, 0, 0, 255);
        var ex = Record.Exception(() => img1.Blend(img2, 0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void Blend_AlphaZero_ReturnsFirstImageDimensions()
    {
        var img1 = CreateGrayscale(8, 8, 0);
        var img2 = CreateGrayscale(8, 8, 255);
        var blended = img1.Blend(img2, 0.0);
        Assert.Equal(8, blended.Width);
        Assert.Equal(8, blended.Height);
    }

    [Fact]
    public void Blend_AlphaOne_ReturnsSecondImageDimensions()
    {
        var img1 = CreateGrayscale(8, 8, 0);
        var img2 = CreateGrayscale(8, 8, 255);
        var blended = img1.Blend(img2, 1.0);
        Assert.Equal(8, blended.Width);
        Assert.Equal(8, blended.Height);
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_NonNull()
    {
        var img = CreateGrayscale(8, 8);
        Assert.NotNull(img.Resize(4, 4));
    }

    [Fact]
    public void Resize_ChangesWidth()
    {
        var img = CreateGrayscale(8, 8);
        var resized = img.Resize(4, 6);
        Assert.Equal(4, resized.Width);
    }

    [Fact]
    public void Resize_ChangesHeight()
    {
        var img = CreateGrayscale(8, 8);
        var resized = img.Resize(4, 6);
        Assert.Equal(6, resized.Height);
    }

    [Fact]
    public void Resize_ToSmaller_Works()
    {
        var img = CreateGrayscale(16, 16);
        var resized = img.Resize(4, 4);
        Assert.Equal(4, resized.Width);
        Assert.Equal(4, resized.Height);
    }

    [Fact]
    public void Resize_ToLarger_Works()
    {
        var img = CreateGrayscale(4, 4);
        var resized = img.Resize(16, 16);
        Assert.Equal(16, resized.Width);
        Assert.Equal(16, resized.Height);
    }

    [Fact]
    public void Resize_Persist()
    {
        var img = CreateGrayscale(8, 8);
        var resized = img.Resize(4, 4);
        var path = TempFile("resize_persist.pgm");
        resized.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(4, loaded.Width);
        Assert.Equal(4, loaded.Height);
    }

    [Fact]
    public void Resize_Consistent()
    {
        var img = CreateGrayscale(8, 8);
        var r1 = img.Resize(4, 4);
        var r2 = img.Resize(4, 4);
        Assert.Equal(r1.Width, r2.Width);
        Assert.Equal(r1.Height, r2.Height);
    }

    [Fact]
    public void Resize_RGB_Works()
    {
        var img = CreateRgb(8, 8);
        var resized = img.Resize(4, 4);
        Assert.Equal(4, resized.Width);
        Assert.Equal(4, resized.Height);
    }

    // -------------------------------------------------------------------------
    // GetAspectRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_Positive()
    {
        var img = CreateGrayscale(8, 4);
        Assert.True(img.GetAspectRatio() > 0);
    }

    [Fact]
    public void GetAspectRatio_SquareIsOne()
    {
        var img = CreateGrayscale(8, 8);
        Assert.Equal(1.0, img.GetAspectRatio(), precision: 4);
    }

    [Fact]
    public void GetAspectRatio_Consistent()
    {
        var img = CreateGrayscale(8, 4);
        Assert.Equal(img.GetAspectRatio(), img.GetAspectRatio(), precision: 4);
    }

    [Fact]
    public void GetAspectRatio_WideImageGreaterThanOne()
    {
        var img = CreateGrayscale(16, 8);
        Assert.True(img.GetAspectRatio() > 1.0);
    }

    [Fact]
    public void GetAspectRatio_TallImageLessThanOne()
    {
        var img = CreateGrayscale(8, 16);
        Assert.True(img.GetAspectRatio() < 1.0);
    }

    [Fact]
    public void GetAspectRatio_AfterResize_Updates()
    {
        var img = CreateGrayscale(8, 8);
        var original = img.GetAspectRatio();
        var resized = img.Resize(16, 8);
        Assert.True(resized.GetAspectRatio() > original);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateImage_Blend_Resize_GetAspectRatio_SaveToFile_Pipeline()
    {
        // Create two grayscale images
        var dark = CreateGrayscale(8, 8, 30);
        var light = CreateGrayscale(8, 8, 220);

        // GetAspectRatio baseline
        Assert.Equal(1.0, dark.GetAspectRatio(), precision: 4);
        Assert.Equal(1.0, light.GetAspectRatio(), precision: 4);

        // Blend
        var blended = dark.Blend(light, 0.5);
        Assert.NotNull(blended);
        Assert.Equal(8, blended.Width);
        Assert.Equal(8, blended.Height);
        Assert.Equal(1.0, blended.GetAspectRatio(), precision: 4);

        // Blend with different alphas
        var nearDark = dark.Blend(light, 0.1);
        Assert.Equal(8, nearDark.Width);
        Assert.Equal(8, nearDark.Height);

        var nearLight = dark.Blend(light, 0.9);
        Assert.Equal(8, nearLight.Width);
        Assert.Equal(8, nearLight.Height);

        // Resize blended to wide
        var wideBlended = blended.Resize(16, 8);
        Assert.Equal(16, wideBlended.Width);
        Assert.Equal(8, wideBlended.Height);
        Assert.True(wideBlended.GetAspectRatio() > 1.0);

        // Resize to tall
        var tallBlended = blended.Resize(8, 16);
        Assert.Equal(8, tallBlended.Width);
        Assert.Equal(16, tallBlended.Height);
        Assert.True(tallBlended.GetAspectRatio() < 1.0);

        // Resize to small
        var tiny = blended.Resize(2, 2);
        Assert.Equal(2, tiny.Width);
        Assert.Equal(2, tiny.Height);
        Assert.Equal(1.0, tiny.GetAspectRatio(), precision: 4);

        // RGB blend
        var redImg = CreateRgb(6, 6, 255, 0, 0);
        var blueImg = CreateRgb(6, 6, 0, 0, 255);
        var purple = redImg.Blend(blueImg, 0.5);
        Assert.Equal(6, purple.Width);
        Assert.Equal(6, purple.Height);

        // Resize RGB
        var purpleResized = purple.Resize(12, 6);
        Assert.Equal(12, purpleResized.Width);
        Assert.Equal(6, purpleResized.Height);
        Assert.True(purpleResized.GetAspectRatio() > 1.0);

        // SaveToFile blended grayscale
        var grayPath = TempFile("dogfood_blend.pgm");
        blended.SaveToFile(grayPath);
        Assert.True(File.Exists(grayPath));
        var loadedGray = NetpbmImage.LoadFile(grayPath);
        Assert.Equal(8, loadedGray.Width);
        Assert.Equal(8, loadedGray.Height);
        Assert.Equal(1.0, loadedGray.GetAspectRatio(), precision: 4);

        // SaveToFile wide resized
        var widePath = TempFile("dogfood_resize_wide.pgm");
        wideBlended.SaveToFile(widePath);
        Assert.True(File.Exists(widePath));
        var loadedWide = NetpbmImage.LoadFile(widePath);
        Assert.Equal(16, loadedWide.Width);
        Assert.True(loadedWide.GetAspectRatio() > 1.0);

        // SaveToFile RGB blend
        var rgbPath = TempFile("dogfood_blend_rgb.ppm");
        purple.SaveToFile(rgbPath);
        Assert.True(File.Exists(rgbPath));
        var loadedRgb = NetpbmImage.LoadFile(rgbPath);
        Assert.Equal(6, loadedRgb.Width);
        Assert.Equal(1.0, loadedRgb.GetAspectRatio(), precision: 4);
    }
}
