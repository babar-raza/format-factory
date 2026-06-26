// Tests for NetpbmImage.DrawRectangle and DrawLine.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R161

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R161: Tests for NetpbmImage.DrawRectangle and DrawLine.
/// DrawRectangle(top, left, h, w, fill, filled): draws filled or outline rectangle.
/// DrawLine(x0, y0, x1, y1, fill): draws a line between two points.
/// Covers: DrawRectangle sets corner pixels; DrawRectangle filled sets interior;
/// DrawRectangle outline leaves interior unchanged; DrawRectangle preserves dimensions;
/// DrawRectangle fill value correct; DrawLine horizontal sets pixels;
/// DrawLine vertical sets pixels; DrawLine does not affect OOB;
/// DrawLine preserves dimensions; DrawLine single point;
/// dogfood Create->DrawRectangle->DrawLine->GetPixel pipeline.
/// </summary>
public class NetpbmR161DrawRectangleAndLineTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill = 0) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    // -------------------------------------------------------------------------
    // DrawRectangle
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_Filled_SetsInteriorPixels()
    {
        var img = MakePgm(10, 10, 0);
        img.DrawRectangle(1, 1, 4, 4, 200, filled: true);
        Assert.Equal(200, img.GetPixel(2, 2)); // interior
        Assert.Equal(200, img.GetPixel(1, 1)); // corner
    }

    [Fact]
    public void DrawRectangle_Outline_SetsCornerPixels()
    {
        var img = MakePgm(10, 10, 0);
        img.DrawRectangle(1, 1, 4, 4, 150, filled: false);
        Assert.Equal(150, img.GetPixel(1, 1));  // top-left corner
        Assert.Equal(150, img.GetPixel(1, 4));  // top-right corner
        Assert.Equal(150, img.GetPixel(4, 1));  // bottom-left corner
    }

    [Fact]
    public void DrawRectangle_Outline_LeavesInteriorUnchanged()
    {
        var img = MakePgm(10, 10, 0);
        img.DrawRectangle(1, 1, 6, 6, 200, filled: false);
        // Interior should still be 0 (not 200)
        Assert.Equal(0, img.GetPixel(3, 3));
    }

    [Fact]
    public void DrawRectangle_PreservesDimensions()
    {
        var img = MakePgm(8, 8, 0);
        img.DrawRectangle(0, 0, 4, 4, 100);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DrawRectangle_Filled_SetsAllPixelsInRegion()
    {
        var img = MakePgm(6, 6, 0);
        img.DrawRectangle(2, 2, 2, 2, 255, filled: true);
        Assert.Equal(255, img.GetPixel(2, 2));
        Assert.Equal(255, img.GetPixel(2, 3));
        Assert.Equal(255, img.GetPixel(3, 2));
        Assert.Equal(255, img.GetPixel(3, 3));
    }

    [Fact]
    public void DrawRectangle_OutsideRect_Unchanged()
    {
        var img = MakePgm(8, 8, 50);
        img.DrawRectangle(2, 2, 3, 3, 200, filled: true);
        Assert.Equal(50, img.GetPixel(0, 0)); // Outside rect
        Assert.Equal(50, img.GetPixel(7, 7)); // Outside rect
    }

    // -------------------------------------------------------------------------
    // DrawLine
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_Horizontal_SetsPixels()
    {
        var img = MakePgm(10, 10, 0);
        img.DrawLine(0, 3, 5, 3, 255); // horizontal line at row 3
        // At least some pixels on the line should be set
        var hasLine = false;
        for (var col = 0; col <= 5; col++)
            if (img.GetPixel(3, col) == 255) { hasLine = true; break; }
        Assert.True(hasLine);
    }

    [Fact]
    public void DrawLine_Vertical_SetsPixels()
    {
        var img = MakePgm(10, 10, 0);
        img.DrawLine(3, 0, 3, 7, 200); // vertical line at col 3
        var hasLine = false;
        for (var row = 0; row <= 7; row++)
            if (img.GetPixel(row, 3) == 200) { hasLine = true; break; }
        Assert.True(hasLine);
    }

    [Fact]
    public void DrawLine_PreservesDimensions()
    {
        var img = MakePgm(8, 6, 0);
        img.DrawLine(0, 0, 7, 5, 100);
        Assert.Equal(8, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void DrawLine_SinglePoint_SetsPixel()
    {
        var img = MakePgm(6, 6, 0);
        img.DrawLine(2, 2, 2, 2, 128); // single point
        Assert.Equal(128, img.GetPixel(2, 2));
    }

    [Fact]
    public void DrawLine_DoesNotCorruptOutsideArea()
    {
        var img = MakePgm(8, 8, 100);
        img.DrawLine(0, 0, 7, 0, 50); // left column
        // Right column should be untouched
        Assert.Equal(100, img.GetPixel(0, 7));
        Assert.Equal(100, img.GetPixel(7, 7));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->DrawRectangle->DrawLine->GetPixel
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_DrawRectangleAndLine_Pipeline()
    {
        var img = MakePgm(12, 12, 0);

        // Draw a filled rectangle
        img.DrawRectangle(1, 1, 5, 5, 150, filled: true);
        Assert.Equal(150, img.GetPixel(1, 1));
        Assert.Equal(150, img.GetPixel(3, 3)); // interior

        // Draw a line across
        img.DrawLine(0, 6, 11, 6, 255);
        var lineHasPixels = false;
        for (var col = 0; col < 12; col++)
            if (img.GetPixel(6, col) == 255) { lineHasPixels = true; break; }
        Assert.True(lineHasPixels);

        // Area outside rect should still be 0
        Assert.Equal(0, img.GetPixel(8, 8));

        // Dimensions preserved
        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);
        Assert.Equal(144, img.Pixels.Length);
    }
}
