// Tests for NetpbmImage.DrawLine, GetHistogram, GetBrightnessMap deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R187

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R187: Tests for NetpbmImage.DrawLine, GetHistogram, GetBrightnessMap deeper coverage.
/// DrawLine(x0,y0,x1,y1,value): draws a line.
/// GetHistogram(): returns 256-element array of pixel value counts.
/// GetBrightnessMap(): returns 2D array of brightness values.
/// Covers: DrawLine horizontal dimensions; DrawLine vertical dimensions;
/// DrawLine modifies pixel at start; DrawLine modifies pixel at end;
/// GetHistogram length is 256; GetHistogram sum equals pixel count;
/// GetHistogram solid image has single non-zero bucket;
/// GetHistogram after DrawLine modifies distribution;
/// GetBrightnessMap non-null; GetBrightnessMap dimensions match image;
/// GetBrightnessMap values in range 0-255; GetBrightnessMap solid image uniform;
/// DrawLine->GetHistogram; GetHistogram bucket for solid value;
/// dogfood Create->DrawLine->GetHistogram->GetBrightnessMap->GetStats pipeline.
/// </summary>
public class NetpbmR187DrawLineAndGetHistogramTests
{
    private static NetpbmImage CreateBlack(int w = 8, int h = 8)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, 0);

    private static NetpbmImage CreateSolid(byte fill, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, fill);

    // -------------------------------------------------------------------------
    // DrawLine
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_Horizontal_DimensionsUnchanged()
    {
        var img = CreateBlack();
        var result = img.DrawLine(0, 0, 7, 0, 200);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void DrawLine_Vertical_DimensionsUnchanged()
    {
        var img = CreateBlack();
        var result = img.DrawLine(4, 0, 4, 7, 150);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void DrawLine_ModifiesStartPixel()
    {
        var img = CreateBlack();
        var result = img.DrawLine(0, 0, 5, 0, 200);
        Assert.Equal(200, result.GetPixel(0, 0));
    }

    [Fact]
    public void DrawLine_ModifiesEndPixel()
    {
        var img = CreateBlack();
        var result = img.DrawLine(0, 3, 7, 3, 150);
        Assert.Equal(150, result.GetPixel(7, 3));
    }

    [Fact]
    public void DrawLine_Diagonal_DimensionsUnchanged()
    {
        var img = CreateBlack();
        var result = img.DrawLine(0, 0, 7, 7, 128);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_Length_Is256()
    {
        var img = CreateSolid(100);
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void GetHistogram_Sum_EqualsPixelCount()
    {
        var img = CreateSolid(100, 4, 4);
        var hist = img.GetHistogram();
        var total = 0;
        for (var i = 0; i < 256; i++) total += hist[i];
        Assert.Equal(img.Width * img.Height, total);
    }

    [Fact]
    public void GetHistogram_SolidImage_SingleNonZeroBucket()
    {
        var img = CreateSolid(200, 4, 4);
        var hist = img.GetHistogram();
        var nonZero = 0;
        for (var i = 0; i < 256; i++) if (hist[i] > 0) nonZero++;
        Assert.Equal(1, nonZero);
    }

    [Fact]
    public void GetHistogram_SolidImage_BucketAtValue()
    {
        var img = CreateSolid(150, 4, 4);
        var hist = img.GetHistogram();
        Assert.Equal(16, hist[150]); // 4x4 pixels all at 150
    }

    [Fact]
    public void GetHistogram_AfterDrawLine_MoreBuckets()
    {
        var img = CreateSolid(0, 8, 8);
        var result = img.DrawLine(0, 0, 7, 0, 255);
        var hist = result.GetHistogram();
        var nonZero = 0;
        for (var i = 0; i < 256; i++) if (hist[i] > 0) nonZero++;
        Assert.True(nonZero >= 2); // at least 0 and 255 buckets
    }

    // -------------------------------------------------------------------------
    // GetBrightnessMap
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessMap_NonNull()
    {
        var img = CreateSolid(100);
        Assert.NotNull(img.GetBrightnessMap());
    }

    [Fact]
    public void GetBrightnessMap_DimensionsMatchImage()
    {
        var img = NetpbmImage.Create(6, 3, NetpbmFormat.Pgm, 128);
        var map = img.GetBrightnessMap();
        Assert.Equal(3, map.GetLength(0)); // rows = height
        Assert.Equal(6, map.GetLength(1)); // cols = width
    }

    [Fact]
    public void GetBrightnessMap_ValuesInRange()
    {
        var img = CreateSolid(128);
        var map = img.GetBrightnessMap();
        for (var row = 0; row < map.GetLength(0); row++)
            for (var col = 0; col < map.GetLength(1); col++)
                Assert.InRange(map[row, col], 0, 255);
    }

    [Fact]
    public void GetBrightnessMap_SolidImage_Uniform()
    {
        var img = CreateSolid(200, 4, 4);
        var map = img.GetBrightnessMap();
        for (var row = 0; row < map.GetLength(0); row++)
            for (var col = 0; col < map.GetLength(1); col++)
                Assert.Equal(200, map[row, col]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->DrawLine->GetHistogram->GetBrightnessMap->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDrawLineGetHistogramGetBrightnessMapGetStats_Pipeline()
    {
        var img = CreateBlack(8, 8);

        // DrawLine
        var lined = img.DrawLine(0, 0, 7, 7, 255);
        Assert.Equal(8, lined.Width);
        Assert.Equal(8, lined.Height);

        // GetHistogram
        var hist = lined.GetHistogram();
        Assert.Equal(256, hist.Length);
        var total = 0;
        for (var i = 0; i < 256; i++) total += hist[i];
        Assert.Equal(64, total); // 8x8 pixels

        // GetBrightnessMap
        var map = lined.GetBrightnessMap();
        Assert.Equal(8, map.GetLength(0));
        Assert.Equal(8, map.GetLength(1));

        // GetStats
        var (mean, min, max) = lined.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
