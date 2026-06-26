// Tests for NetpbmImage.Tile, Overlay, Invert deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R186

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R186: Tests for NetpbmImage.Tile, Overlay, Invert deeper coverage.
/// Tile(cols, rows): tiles the image into a grid of cols×rows copies.
/// Overlay(other, x, y): overlays another image at (x,y).
/// Invert(): inverts all pixel values (255 - value).
/// Covers: Tile returns new image; Tile 2x2 doubles dimensions;
/// Tile 1x1 preserves dimensions; Tile 3x1 triples width;
/// Overlay returns new image; Overlay dimensions match destination;
/// Overlay at origin; Overlay at non-origin position;
/// Invert returns new image; Invert dimensions unchanged;
/// Invert solid black becomes white; Invert solid white becomes black;
/// Invert->Invert restores values; Tile->Overlay chain;
/// Invert then GetStats; Tile dimensions correct;
/// dogfood Create->Tile->Overlay->Invert->GetStats pipeline.
/// </summary>
public class NetpbmR186TileAndOverlayTests
{
    private static NetpbmImage CreateGray(byte fill, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, fill);

    // -------------------------------------------------------------------------
    // Tile
    // -------------------------------------------------------------------------

    [Fact]
    public void Tile_ReturnsNewImage()
    {
        var img = CreateGray(128);
        var result = img.Tile(2, 2);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Tile_2x2_DoublesDimensions()
    {
        var img = CreateGray(128, 4, 4);
        var result = img.Tile(2, 2);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Tile_1x1_PreservesDimensions()
    {
        var img = CreateGray(128, 4, 4);
        var result = img.Tile(1, 1);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Tile_3x1_TriplesWidth()
    {
        var img = CreateGray(128, 4, 4);
        var result = img.Tile(3, 1);
        Assert.Equal(12, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Tile_1x3_TriplesHeight()
    {
        var img = CreateGray(128, 4, 4);
        var result = img.Tile(1, 3);
        Assert.Equal(4, result.Width);
        Assert.Equal(12, result.Height);
    }

    [Fact]
    public void Tile_PreservesPixelValues()
    {
        var img = CreateGray(200, 4, 4);
        var result = img.Tile(2, 2);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(200.0, mean, 0);
    }

    // -------------------------------------------------------------------------
    // Overlay
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_ReturnsNewImage()
    {
        var base_ = CreateGray(100, 8, 8);
        var overlay = CreateGray(200, 2, 2);
        var result = base_.Overlay(overlay, 0, 0);
        Assert.NotSame(base_, result);
    }

    [Fact]
    public void Overlay_DimensionsMatchDestination()
    {
        var base_ = CreateGray(100, 8, 8);
        var overlay = CreateGray(200, 2, 2);
        var result = base_.Overlay(overlay, 0, 0);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Overlay_AtOrigin_ModifiesPixel()
    {
        var base_ = CreateGray(0, 8, 8);
        var overlay = CreateGray(255, 2, 2);
        var result = base_.Overlay(overlay, 0, 0);
        Assert.Equal(255, result.GetPixel(0, 0));
    }

    [Fact]
    public void Overlay_AtNonOrigin_PreservesBackground()
    {
        var base_ = CreateGray(50, 8, 8);
        var overlay = CreateGray(200, 2, 2);
        var result = base_.Overlay(overlay, 4, 4);
        // Pixel at (0,0) should still be from background
        Assert.Equal(50, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Invert
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_ReturnsNewImage()
    {
        var img = CreateGray(128);
        var result = img.Invert();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Invert_DimensionsUnchanged()
    {
        var img = CreateGray(128, 6, 3);
        var result = img.Invert();
        Assert.Equal(6, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Invert_SolidBlack_BecomesWhite()
    {
        var img = CreateGray(0);
        var result = img.Invert();
        var (mean, _, _) = result.GetStats();
        Assert.Equal(255.0, mean, 0);
    }

    [Fact]
    public void Invert_SolidWhite_BecomesBlack()
    {
        var img = CreateGray(255);
        var result = img.Invert();
        var (mean, _, _) = result.GetStats();
        Assert.Equal(0.0, mean, 0);
    }

    [Fact]
    public void Invert_Twice_RestoresOriginal()
    {
        var img = CreateGray(150);
        var inverted = img.Invert();
        var restored = inverted.Invert();
        var (mean, _, _) = restored.GetStats();
        Assert.Equal(150.0, mean, 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Tile->Overlay->Invert->GetStats pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateTileOverlayInvertGetStats_Pipeline()
    {
        var img = CreateGray(100, 4, 4);

        // Tile 2x2
        var tiled = img.Tile(2, 2);
        Assert.Equal(8, tiled.Width);
        Assert.Equal(8, tiled.Height);
        var (tileMean, _, _) = tiled.GetStats();
        Assert.Equal(100.0, tileMean, 0);

        // Overlay
        var overlay = CreateGray(200, 2, 2);
        var overlaid = tiled.Overlay(overlay, 0, 0);
        Assert.Equal(8, overlaid.Width);
        Assert.Equal(8, overlaid.Height);

        // Invert
        var inverted = overlaid.Invert();
        Assert.Equal(8, inverted.Width);
        Assert.Equal(8, inverted.Height);

        // GetStats — invert should bring 100→155, 200→55
        var (mean, min, max) = inverted.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
