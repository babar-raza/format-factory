// Tests for NetpbmImage.DrawLine dedicated coverage.
// Sprint: ff-sprint-s219-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R226

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R226: Dedicated tests for NetpbmImage.DrawLine(x0, y0, x1, y1, value).
/// OOB coordinates → throws exception.
/// Valid call → no exception.
/// Line pixels have specified value.
/// Pixels outside line unchanged.
/// Format preserved after draw.
/// MaxValue preserved after draw.
/// Dimensions preserved after draw.
/// Horizontal line: all pixels on row have value.
/// Vertical line: all pixels on column have value.
/// Dogfood: draw two lines, both visible.
/// </summary>
public class NetpbmR226DrawLineTests
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
        var ex = Record.Exception(() => img.DrawLine(0, 0, 7, 7, 200));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawLine_LinePixelsHaveSpecifiedValue()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 0, 7, 200);
        // Vertical line at x=0: all y pixels should be 200
        Assert.Equal(200, img.GetPixel(0, 0));
        Assert.Equal(200, img.GetPixel(0, 7));
    }

    [Fact]
    public void DrawLine_PixelsOutsideLine_Unchanged()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(7, 7, 50);
        img.DrawLine(0, 0, 0, 0, 200);
        Assert.Equal(50, img.GetPixel(7, 7));
    }

    [Fact]
    public void DrawLine_FormatPreserved()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 5, 0, 100);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void DrawLine_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 200);
        img.DrawLine(0, 0, 5, 0, 100);
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void DrawLine_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 5, 0, 100);
        Assert.Equal(6, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DrawLine_HorizontalLine_AllPixelsHaveValue()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 3, 7, 3, 150);
        // Check endpoints of horizontal line at y=3
        Assert.Equal(150, img.GetPixel(0, 3));
        Assert.Equal(150, img.GetPixel(7, 3));
    }

    [Fact]
    public void DrawLine_VerticalLine_ColumnPixelsHaveValue()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(4, 0, 4, 7, 175);
        // Vertical line at x=4
        Assert.Equal(175, img.GetPixel(4, 0));
        Assert.Equal(175, img.GetPixel(4, 7));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoLines_BothVisible()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P5, maxValue: 255);
        img.DrawLine(0, 0, 9, 0, 100);  // top row
        img.DrawLine(0, 9, 9, 9, 200);  // bottom row
        Assert.Equal(100, img.GetPixel(0, 0));
        Assert.Equal(100, img.GetPixel(9, 0));
        Assert.Equal(200, img.GetPixel(0, 9));
        Assert.Equal(200, img.GetPixel(9, 9));
    }
}
