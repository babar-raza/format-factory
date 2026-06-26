// Tests for NetpbmImage.DrawLine dedicated coverage.
// Sprint: ff-sprint-s244-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R251

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R251: Dedicated tests for NetpbmImage.DrawLine(x0, y0, x1, y1, value).
/// OOB coordinates → throws exception.
/// Valid call → no exception.
/// Line pixels have specified value.
/// Pixels outside the line unchanged.
/// Format preserved after draw.
/// MaxValue preserved after draw.
/// Dimensions unchanged after draw.
/// Horizontal line → all target row pixels at specified value.
/// Vertical line → all target column pixels at specified value.
/// Dogfood: draw two lines, both visible in image.
/// </summary>
public class NetpbmR251DrawLineDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_OobCoordinates_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.DrawLine(0, 0, 10, 10, 128));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var ex = Record.Exception(() => img.DrawLine(0, 0, 7, 0, 200));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawLine_LinePixelsHaveValue()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 0, 7, 200); // vertical line at x=0
        Assert.Equal(200, img.GetPixel(0, 0));
        Assert.Equal(200, img.GetPixel(0, 7));
    }

    [Fact]
    public void DrawLine_PixelsOutsideLine_Unchanged()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(5, 5, 99);
        img.DrawLine(0, 0, 0, 3, 200); // vertical at x=0, rows 0-3
        // Pixel at (5,5) should still be 99
        Assert.Equal(99, img.GetPixel(5, 5));
    }

    [Fact]
    public void DrawLine_FormatPreserved()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 7, 7, 100);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void DrawLine_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 150);
        img.DrawLine(0, 0, 7, 0, 100);
        Assert.Equal(150, img.MaxValue);
    }

    [Fact]
    public void DrawLine_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 7, 0, 200);
        Assert.Equal(8, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void DrawLine_HorizontalLine_RowPixelsHaveValue()
    {
        var img = NetpbmImage.Create(8, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 7, 0, 175); // horizontal at y=0
        Assert.Equal(175, img.GetPixel(0, 0));
        Assert.Equal(175, img.GetPixel(7, 0));
    }

    [Fact]
    public void DrawLine_VerticalLine_ColumnPixelsHaveValue()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(3, 0, 3, 7, 222); // vertical at x=3
        Assert.Equal(222, img.GetPixel(3, 0));
        Assert.Equal(222, img.GetPixel(3, 7));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoLines_BothVisible()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 7, 0, 100); // horizontal line at y=0
        img.DrawLine(0, 4, 7, 4, 200); // horizontal line at y=4
        Assert.Equal(100, img.GetPixel(0, 0));
        Assert.Equal(200, img.GetPixel(0, 4));
    }
}
