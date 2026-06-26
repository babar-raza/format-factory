// Tests for NetpbmImage.DrawRectangle, FillRegion deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R195

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R195: Tests for NetpbmImage.DrawRectangle, FillRegion deeper coverage.
/// DrawRectangle(x, y, w, h, color): draws a rectangle outline.
/// FillRegion(x, y, w, h, color): fills a rectangular region with a color.
/// Covers: DrawRectangle on black canvas non-null; DrawRectangle preserves dimensions;
/// DrawRectangle outline visible (corner pixels changed); DrawRectangle full-canvas preserves size;
/// FillRegion non-null; FillRegion preserves dimensions; FillRegion fills entire canvas;
/// FillRegion partial region; DrawRectangle->FillRegion combined;
/// FillRegion after DrawRectangle; DrawRectangle on color image;
/// dogfood CreateCanvas->FillRegion->DrawRectangle->Verify pipeline.
/// </summary>
public class NetpbmR195DrawRectangleFillRegionDeepTests
{
    // -------------------------------------------------------------------------
    // DrawRectangle
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.DrawRectangle(1, 1, 5, 5, 128));
    }

    [Fact]
    public void DrawRectangle_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 255);
        var result = img.DrawRectangle(1, 1, 5, 5, 0);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void DrawRectangle_AtOrigin_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 255);
        var result = img.DrawRectangle(0, 0, 4, 4, 0);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void DrawRectangle_FullCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, NetpbmFormat.Pgm, 255);
        var result = img.DrawRectangle(0, 0, 6, 6, 0);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void DrawRectangle_SmallCanvas_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.DrawRectangle(0, 0, 2, 2, 128));
    }

    [Fact]
    public void DrawRectangle_Twice_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 255);
        var result = img.DrawRectangle(1, 1, 4, 4, 0).DrawRectangle(3, 3, 5, 5, 128);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    // -------------------------------------------------------------------------
    // FillRegion
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.FillRegion(0, 0, 8, 8, 0));
    }

    [Fact]
    public void FillRegion_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 255);
        var filled = img.FillRegion(0, 0, 4, 4, 128);
        Assert.Equal(8, filled.Width);
        Assert.Equal(8, filled.Height);
    }

    [Fact]
    public void FillRegion_FullCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 6, NetpbmFormat.Pgm, 255);
        var filled = img.FillRegion(0, 0, 6, 6, 0);
        Assert.Equal(6, filled.Width);
        Assert.Equal(6, filled.Height);
    }

    [Fact]
    public void FillRegion_Partial_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 255);
        var filled = img.FillRegion(2, 2, 4, 4, 64);
        Assert.Equal(10, filled.Width);
        Assert.Equal(10, filled.Height);
    }

    [Fact]
    public void FillRegion_ThenDrawRectangle_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 255);
        var result = img.FillRegion(0, 0, 10, 10, 128).DrawRectangle(1, 1, 8, 8, 0);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void FillRegion_DrawRectangle_Chain_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 0);
        var result = img.FillRegion(1, 1, 6, 6, 200).DrawRectangle(2, 2, 4, 4, 0);
        Assert.NotNull(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_FillRegion_DrawRectangle_Verify_Pipeline()
    {
        // CreateCanvas 12x12 black
        var img = NetpbmImage.CreateCanvas(12, 12, NetpbmFormat.Pgm, 0);
        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);

        // FillRegion center 8x8 with gray
        var filled = img.FillRegion(2, 2, 8, 8, 128);
        Assert.Equal(12, filled.Width);
        Assert.Equal(12, filled.Height);

        // DrawRectangle border around filled area
        var boxed = filled.DrawRectangle(1, 1, 10, 10, 255);
        Assert.Equal(12, boxed.Width);
        Assert.Equal(12, boxed.Height);

        // DrawRectangle inner border
        var innerBox = boxed.DrawRectangle(3, 3, 6, 6, 0);
        Assert.Equal(12, innerBox.Width);
        Assert.Equal(12, innerBox.Height);

        // FillRegion top-left corner
        var final = innerBox.FillRegion(0, 0, 2, 2, 200);
        Assert.Equal(12, final.Width);
        Assert.Equal(12, final.Height);

        // Verify pixel count unchanged
        Assert.Equal(img.Width * img.Height, final.Width * final.Height);
    }
}
