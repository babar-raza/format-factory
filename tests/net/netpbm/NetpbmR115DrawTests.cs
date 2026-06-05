using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R115 Train A/B: DrawRectangle + GetBrightnessMap — drawing primitives and brightness analysis.
/// </summary>
public class NetpbmR115DrawTests
{
    [Fact]
    public void DrawRectangle_Filled_SetsPixels()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawRectangle(top: 2, left: 2, rectHeight: 4, rectWidth: 4, fill: 200);
        // Interior pixel should be 200
        Assert.Equal(200, img.GetPixel(3, 3));
        // Outside should remain 0
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    [Fact]
    public void DrawRectangle_OutlineOnly_BorderPixelsSet()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawRectangle(top: 1, left: 1, rectHeight: 6, rectWidth: 6, fill: 255, filled: false);
        // Top-left corner of border
        Assert.Equal(255, img.GetPixel(1, 1));
        // Interior should remain 0
        Assert.Equal(0, img.GetPixel(3, 3));
    }

    [Fact]
    public void DrawRectangle_ClipsToImageBounds()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P2, fill: 0);
        // Draw a rect that extends outside the image — should not throw
        img.DrawRectangle(top: 3, left: 3, rectHeight: 10, rectWidth: 10, fill: 100);
        Assert.Equal(100, img.GetPixel(4, 4)); // corner pixel
    }

    [Fact]
    public void DrawRectangle_ZeroSize_NoEffect()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawRectangle(top: 1, left: 1, rectHeight: 0, rectWidth: 3, fill: 200);
        Assert.All(img.Pixels, p => Assert.Equal(0, p));
    }

    [Fact]
    public void DrawRectangle_ThrowsOnColorImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P3, fill: 0);
        Assert.Throws<InvalidOperationException>(() =>
            img.DrawRectangle(0, 0, 3, 3, fill: 100));
    }

    [Fact]
    public void GetBrightnessMap_Grayscale_NormalisedCorrectly()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, fill: 128);
        img.MaxValue = 255;
        var map = img.GetBrightnessMap();
        Assert.Equal(4, map.Length);
        Assert.All(map, v => Assert.InRange(v, 0.0, 1.0));
        Assert.All(map, v => Assert.Equal(128.0 / 255.0, v, precision: 4));
    }

    [Fact]
    public void GetBrightnessMap_Black_AllZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2, fill: 0);
        var map = img.GetBrightnessMap();
        Assert.All(map, v => Assert.Equal(0.0, v));
    }

    [Fact]
    public void GetBrightnessMap_White_AllOne()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, fill: 255);
        img.MaxValue = 255;
        var map = img.GetBrightnessMap();
        Assert.All(map, v => Assert.InRange(v, 0.99, 1.01));
    }

    [Fact]
    public void DrawThenGetBrightness_Pipeline_Correct()
    {
        // Dogfood: Create + Draw + GetBrightnessMap pipeline
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P2, fill: 0);
        img.MaxValue = 255;
        img.DrawRectangle(top: 2, left: 2, rectHeight: 4, rectWidth: 4, fill: 255);
        var map = img.GetBrightnessMap();
        // Pixel inside rect: brightness = 1.0
        Assert.Equal(1.0, map[3 * 8 + 3], precision: 3);
        // Pixel outside rect: brightness = 0.0
        Assert.Equal(0.0, map[0 * 8 + 0], precision: 3);
    }
}
