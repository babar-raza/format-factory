using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R116 Train A: DrawLine — Bresenham drawing primitive on PGM images.
/// </summary>
public class NetpbmR116DrawLineTests
{
    [Fact]
    public void DrawLine_Horizontal_SetsPixels()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawLine(0, 3, 9, 3, fill: 200); // row 3, col 0..9
        Assert.Equal(200, img.GetPixel(3, 0));
        Assert.Equal(200, img.GetPixel(3, 5));
        Assert.Equal(200, img.GetPixel(3, 9));
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    [Fact]
    public void DrawLine_Vertical_SetsPixels()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawLine(4, 0, 4, 9, fill: 150); // col 4, row 0..9
        Assert.Equal(150, img.GetPixel(0, 4));
        Assert.Equal(150, img.GetPixel(9, 4));
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    [Fact]
    public void DrawLine_Diagonal_SetsEndpoints()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawLine(0, 0, 9, 9, fill: 128); // diagonal from (0,0) to (9,9)
        Assert.Equal(128, img.GetPixel(0, 0));
        Assert.Equal(128, img.GetPixel(9, 9));
    }

    [Fact]
    public void DrawLine_SinglePoint_SetsOnePixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawLine(2, 3, 2, 3, fill: 255);
        Assert.Equal(255, img.GetPixel(3, 2));
    }

    [Fact]
    public void DrawLine_OutOfBounds_DoesNotThrow()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P2, fill: 0);
        // Should not throw even when coordinates are outside image
        img.DrawLine(-5, -5, 15, 15, fill: 100);
        // Pixels inside bounds should be set
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void DrawLine_ThrowsOnColorImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P3, fill: 0);
        Assert.Throws<InvalidOperationException>(() => img.DrawLine(0, 0, 4, 4, fill: 100));
    }

    [Fact]
    public void DrawLine_DogfoodPipeline_DrawAndBrightnessMap()
    {
        // Dogfood: Create PGM → DrawLine → GetBrightnessMap → verify line pixels
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P2, fill: 0);
        img.MaxValue = 255;
        img.DrawLine(0, 4, 7, 4, fill: 255); // horizontal line at row 4
        var map = img.GetBrightnessMap();
        // Row 4, col 0 brightness = 1.0
        Assert.Equal(1.0, map[4 * 8 + 0], precision: 3);
        // Row 0, col 0 brightness = 0.0
        Assert.Equal(0.0, map[0 * 8 + 0], precision: 3);
    }

    [Fact]
    public void DrawRectangleThenLine_Pipeline()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P2, fill: 0);
        img.DrawRectangle(top: 1, left: 1, rectHeight: 8, rectWidth: 8, fill: 100);
        img.DrawLine(0, 5, 9, 5, fill: 200); // horizontal line overdraws middle
        Assert.Equal(200, img.GetPixel(5, 5));
        Assert.Equal(100, img.GetPixel(2, 2));
    }
}
