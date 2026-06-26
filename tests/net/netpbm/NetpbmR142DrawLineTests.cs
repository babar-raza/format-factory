// Tests for NetpbmImage.DrawLine.
// Sprint: ff-sprint-s142-dotnet-deepening-20260627
// Ledger: PC-NETPBM-R142

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R142: Tests for NetpbmImage.DrawLine (Bresenham's algorithm, PGM-only).
/// DrawLine sets pixels along a line from (x0,y0) to (x1,y1) using Bresenham's algorithm.
/// Only supported for PGM images (PGM_P2 or PGM_P5); throws on PPM.
/// Covers: DrawLine on PPM throws InvalidOperationException; horizontal line sets endpoints;
/// vertical line sets endpoints; diagonal line sets start pixel; single-point line (same coords) sets pixel;
/// DrawLine value stored correctly; DrawLine from (0,0) to (0,0) sets pixel;
/// DrawLine clamps out-of-bound coordinates (clipping by bounds check);
/// dogfood Create->DrawLine->GetPixel verifies both endpoints; Create->DrawLine->DrawRectangle pipeline.
/// </summary>
public class NetpbmR142DrawLineTests
{
    // -------------------------------------------------------------------------
    // Format guard: PPM throws
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_OnPpmImage_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        Assert.Throws<InvalidOperationException>(() => img.DrawLine(0, 0, 3, 3, 200));
    }

    // -------------------------------------------------------------------------
    // DrawLine functional tests on PGM
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_HorizontalLine_SetsStartPixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.DrawLine(0, 2, 4, 2, 128);
        Assert.Equal(128, img.GetPixel(2, 0)); // row=2, col=0
    }

    [Fact]
    public void DrawLine_HorizontalLine_SetsEndPixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.DrawLine(0, 2, 4, 2, 128);
        Assert.Equal(128, img.GetPixel(2, 4)); // row=2, col=4
    }

    [Fact]
    public void DrawLine_VerticalLine_SetsTopPixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.DrawLine(2, 0, 2, 4, 200);
        Assert.Equal(200, img.GetPixel(0, 2)); // row=0, col=2
    }

    [Fact]
    public void DrawLine_VerticalLine_SetsBottomPixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.DrawLine(2, 0, 2, 4, 200);
        Assert.Equal(200, img.GetPixel(4, 2)); // row=4, col=2
    }

    [Fact]
    public void DrawLine_DiagonalLine_SetsStartPixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.DrawLine(0, 0, 4, 4, 99);
        Assert.Equal(99, img.GetPixel(0, 0)); // start = row=0, col=0
    }

    [Fact]
    public void DrawLine_SinglePointLine_SetsPixel()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.DrawLine(2, 2, 2, 2, 77);
        Assert.Equal(77, img.GetPixel(2, 2));
    }

    [Fact]
    public void DrawLine_OutOfBoundsCoordinates_DoesNotThrow()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        // Line extends beyond image bounds — out-of-bounds pixels are clipped by bounds check
        var ex = Record.Exception(() => img.DrawLine(-2, -2, 10, 10, 50));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create -> DrawLine -> GetPixel -> DrawRectangle pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DrawLine_GetPixel_BothEndpointsVerified()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        img.DrawLine(0, 0, 5, 0, 150); // horizontal line on row 0

        Assert.Equal(150, img.GetPixel(0, 0)); // start
        Assert.Equal(150, img.GetPixel(0, 5)); // end
    }

    [Fact]
    public void DogfoodPipeline_DrawLine_ThenDrawRectangle_BothOperationsSucceed()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        img.DrawLine(0, 0, 5, 5, 100);
        img.DrawRectangle(1, 1, 3, 3, 200);

        // Rectangle fill overwrites diagonal in [1..3, 1..3]
        Assert.Equal(200, img.GetPixel(2, 2));
        // Diagonal corner (0,0) is untouched by rectangle
        Assert.Equal(100, img.GetPixel(0, 0));
    }
}
