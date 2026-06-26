// Tests for NetpbmImage.GetPixelColor, SetPixelColor deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R205

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R205: Tests for NetpbmImage.GetPixelColor, SetPixelColor deeper coverage.
/// GetPixelColor(x, y): returns the pixel value at the given coordinates.
/// SetPixelColor(x, y, value): sets the pixel at the given coordinates to the given value.
/// Covers: GetPixelColor returns fill value for uniform canvas; GetPixelColor corner pixels;
/// GetPixelColor after DrawLine returns line value; SetPixelColor changes pixel value;
/// SetPixelColor non-null result; SetPixelColor preserves dimensions;
/// SetPixelColor does not change other pixels; SetPixelColor chain at multiple coords;
/// GetPixelColor after SetPixelColor returns new value; SetPixelColor then GetHistogram changes;
/// dogfood CreateCanvas->SetPixelColor->GetPixelColor->GetHistogram->Verify pipeline.
/// </summary>
public class NetpbmR205GetPixelColorAndSetPixelColorDeepTests
{
    // -------------------------------------------------------------------------
    // GetPixelColor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelColor_UniformCanvas_ReturnsFillValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 128);
        Assert.Equal(128, img.GetPixelColor(0, 0));
    }

    [Fact]
    public void GetPixelColor_TopLeftCorner()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        Assert.Equal(200, img.GetPixelColor(0, 0));
    }

    [Fact]
    public void GetPixelColor_BottomRightCorner()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        Assert.Equal(200, img.GetPixelColor(5, 3));
    }

    [Fact]
    public void GetPixelColor_CenterPixel()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 150);
        Assert.Equal(150, img.GetPixelColor(3, 2));
    }

    [Fact]
    public void GetPixelColor_AfterDrawLine_ReturnsLineValue()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 200);
        // Draw horizontal line at y=4 with value 50
        var withLine = img.DrawLine(0, 4, 7, 4, 50);
        Assert.Equal(50, withLine.GetPixelColor(0, 4));
        Assert.Equal(50, withLine.GetPixelColor(7, 4));
    }

    // -------------------------------------------------------------------------
    // SetPixelColor
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixelColor_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 200);
        Assert.NotNull(img.SetPixelColor(1, 1, 100));
    }

    [Fact]
    public void SetPixelColor_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        var result = img.SetPixelColor(2, 2, 50);
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void SetPixelColor_ChangesPixelValue()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 200);
        var result = img.SetPixelColor(1, 1, 50);
        Assert.Equal(50, result.GetPixelColor(1, 1));
    }

    [Fact]
    public void SetPixelColor_DoesNotChangeOtherPixels()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 200);
        var result = img.SetPixelColor(1, 1, 50);
        // All other pixels should remain 200
        Assert.Equal(200, result.GetPixelColor(0, 0));
        Assert.Equal(200, result.GetPixelColor(3, 3));
        Assert.Equal(200, result.GetPixelColor(2, 2));
    }

    [Fact]
    public void SetPixelColor_Chain_MultipleCoords()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, NetpbmFormat.Pgm, 200);
        var result = img
            .SetPixelColor(0, 0, 10)
            .SetPixelColor(2, 2, 100)
            .SetPixelColor(4, 4, 200);
        Assert.Equal(10, result.GetPixelColor(0, 0));
        Assert.Equal(100, result.GetPixelColor(2, 2));
        Assert.Equal(200, result.GetPixelColor(4, 4));
    }

    [Fact]
    public void SetPixelColor_AllCorners_Correct()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 255);
        var result = img
            .SetPixelColor(0, 0, 10)
            .SetPixelColor(5, 0, 20)
            .SetPixelColor(0, 3, 30)
            .SetPixelColor(5, 3, 40);
        Assert.Equal(10, result.GetPixelColor(0, 0));
        Assert.Equal(20, result.GetPixelColor(5, 0));
        Assert.Equal(30, result.GetPixelColor(0, 3));
        Assert.Equal(40, result.GetPixelColor(5, 3));
    }

    [Fact]
    public void SetPixelColor_Zero_SetsBlack()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 255);
        var result = img.SetPixelColor(2, 2, 0);
        Assert.Equal(0, result.GetPixelColor(2, 2));
    }

    [Fact]
    public void SetPixelColor_MaxValue_SetsWhite()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 0);
        var result = img.SetPixelColor(2, 2, 255);
        Assert.Equal(255, result.GetPixelColor(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_SetPixelColor_GetPixelColor_GetHistogram_Verify_Pipeline()
    {
        // CreateCanvas
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        Assert.Equal(200, img.GetPixelColor(0, 0));

        // SetPixelColor at multiple spots
        var modified = img
            .SetPixelColor(0, 0, 50)
            .SetPixelColor(1, 0, 100)
            .SetPixelColor(2, 0, 150)
            .SetPixelColor(3, 0, 50)
            .SetPixelColor(4, 0, 100);

        // GetPixelColor verification
        Assert.Equal(50, modified.GetPixelColor(0, 0));
        Assert.Equal(100, modified.GetPixelColor(1, 0));
        Assert.Equal(150, modified.GetPixelColor(2, 0));
        Assert.Equal(50, modified.GetPixelColor(3, 0));
        Assert.Equal(100, modified.GetPixelColor(4, 0));
        // Unchanged pixel
        Assert.Equal(200, modified.GetPixelColor(5, 0));
        Assert.Equal(200, modified.GetPixelColor(0, 1));

        // GetHistogram should reflect all distinct values
        var hist = modified.GetHistogram();
        Assert.True(hist.ContainsKey(50));
        Assert.True(hist.ContainsKey(100));
        Assert.True(hist.ContainsKey(150));
        Assert.True(hist.ContainsKey(200));

        // Pixel counts
        Assert.Equal(2, hist[50]);  // positions (0,0) and (3,0)
        Assert.Equal(2, hist[100]); // positions (1,0) and (4,0)
        Assert.Equal(1, hist[150]); // position (2,0)

        // Total pixels
        var total = 0;
        foreach (var c in hist.Values) total += c;
        Assert.Equal(24, total); // 6x4
    }
}
