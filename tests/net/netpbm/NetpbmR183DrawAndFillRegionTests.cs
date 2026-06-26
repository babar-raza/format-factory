// Tests for NetpbmImage.DrawRectangle, DrawLine, FillRegion, CopyRegion deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R183

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R183: Tests for NetpbmImage.DrawRectangle, DrawLine, FillRegion, CopyRegion deeper coverage.
/// DrawRectangle(x,y,w,h,value): draws a rectangle outline.
/// DrawLine(x0,y0,x1,y1,value): draws a line between two points.
/// FillRegion(x,y,w,h,value): fills a rectangular region.
/// CopyRegion(src,dstX,dstY,srcX,srcY,w,h): copies a region from source image.
/// Covers: DrawRectangle returns new image; DrawRectangle dimensions unchanged;
/// DrawRectangle modifies corner pixels; DrawLine returns new image;
/// DrawLine dimensions unchanged; DrawLine modifies along axis;
/// FillRegion returns new image; FillRegion dimensions unchanged;
/// FillRegion fills expected pixels; CopyRegion returns new image;
/// CopyRegion dimensions match destination; CopyRegion copies pixel values;
/// DrawRectangle then FillRegion chain; FillRegion with boundary values;
/// dogfood Create->FillRegion->DrawRectangle->DrawLine->GetStats pipeline.
/// </summary>
public class NetpbmR183DrawAndFillRegionTests
{
    private static NetpbmImage CreateBlack(int w = 8, int h = 8)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, 0);

    private static NetpbmImage CreateGray(byte fill = 128, int w = 8, int h = 8)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, fill);

    // -------------------------------------------------------------------------
    // DrawRectangle
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_ReturnsNewImage()
    {
        var img = CreateBlack();
        var result = img.DrawRectangle(1, 1, 4, 4, 255);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void DrawRectangle_DimensionsUnchanged()
    {
        var img = CreateBlack(8, 8);
        var result = img.DrawRectangle(0, 0, 4, 4, 255);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void DrawRectangle_CornerPixel_HasValue()
    {
        var img = CreateBlack();
        var result = img.DrawRectangle(2, 2, 3, 3, 200);
        // Top-left corner of rectangle at (2,2)
        Assert.Equal(200, result.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // DrawLine
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_ReturnsNewImage()
    {
        var img = CreateBlack();
        var result = img.DrawLine(0, 0, 7, 7, 255);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void DrawLine_DimensionsUnchanged()
    {
        var img = CreateBlack(8, 8);
        var result = img.DrawLine(0, 0, 7, 0, 128);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void DrawLine_HorizontalLine_StartPixelSet()
    {
        var img = CreateBlack();
        var result = img.DrawLine(0, 0, 5, 0, 150);
        Assert.Equal(150, result.GetPixel(0, 0));
    }

    [Fact]
    public void DrawLine_VerticalLine_TopPixelSet()
    {
        var img = CreateBlack();
        var result = img.DrawLine(3, 0, 3, 6, 180);
        Assert.Equal(180, result.GetPixel(3, 0));
    }

    // -------------------------------------------------------------------------
    // FillRegion
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_ReturnsNewImage()
    {
        var img = CreateBlack();
        var result = img.FillRegion(0, 0, 4, 4, 255);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void FillRegion_DimensionsUnchanged()
    {
        var img = CreateBlack(8, 8);
        var result = img.FillRegion(0, 0, 4, 4, 200);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void FillRegion_FillsExpectedPixels()
    {
        var img = CreateBlack();
        var result = img.FillRegion(0, 0, 8, 8, 200);
        // All pixels should be 200
        var (mean, min, _) = result.GetStats();
        Assert.Equal(200.0, mean, 0);
        Assert.Equal(200, min);
    }

    [Fact]
    public void FillRegion_BoundaryValue_Zero()
    {
        var img = CreateGray(255);
        var result = img.FillRegion(0, 0, 8, 8, 0);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(0.0, mean, 0);
    }

    // -------------------------------------------------------------------------
    // CopyRegion
    // -------------------------------------------------------------------------

    [Fact]
    public void CopyRegion_ReturnsNewImage()
    {
        var src = CreateGray(200);
        var dst = CreateBlack();
        var result = dst.CopyRegion(src, 0, 0, 0, 0, 4, 4);
        Assert.NotSame(dst, result);
    }

    [Fact]
    public void CopyRegion_DimensionsMatchDestination()
    {
        var src = CreateGray(200, 8, 8);
        var dst = CreateBlack(8, 8);
        var result = dst.CopyRegion(src, 0, 0, 0, 0, 4, 4);
        Assert.Equal(dst.Width, result.Width);
        Assert.Equal(dst.Height, result.Height);
    }

    [Fact]
    public void CopyRegion_CopiesPixelValues()
    {
        var src = NetpbmImage.Create(8, 8, NetpbmFormat.Pgm, 0);
        src.SetPixel(0, 0, 250);
        var dst = CreateBlack();
        var result = dst.CopyRegion(src, 0, 0, 0, 0, 1, 1);
        Assert.Equal(250, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->FillRegion->DrawRectangle->DrawLine->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateFillRectLineGetStats_Pipeline()
    {
        var img = CreateBlack(8, 8);

        // FillRegion — fill with mid-gray
        var filled = img.FillRegion(0, 0, 8, 8, 128);
        var (meanFilled, _, _) = filled.GetStats();
        Assert.Equal(128.0, meanFilled, 0);

        // DrawRectangle
        var rectImg = filled.DrawRectangle(1, 1, 6, 6, 255);
        Assert.Equal(8, rectImg.Width);
        Assert.Equal(8, rectImg.Height);
        // Corner should be 255
        Assert.Equal(255, rectImg.GetPixel(1, 1));

        // DrawLine
        var lineImg = rectImg.DrawLine(0, 0, 7, 7, 0);
        Assert.Equal(8, lineImg.Width);
        Assert.Equal(8, lineImg.Height);

        // GetStats
        var (mean, min, max) = lineImg.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
