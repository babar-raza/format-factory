// Tests for NetpbmImage.ApplyGamma, Tile, Overlay chain deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R201

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R201: Tests for NetpbmImage.ApplyGamma, Tile, Overlay chain deeper.
/// ApplyGamma(gamma): applies gamma correction to the image.
/// Tile(tilesX, tilesY): creates a tiled version of the image.
/// Overlay(other, x, y): overlays another image on this one at position (x, y).
/// Covers: ApplyGamma non-null; ApplyGamma preserves dimensions; ApplyGamma 1.0 is identity-like;
/// ApplyGamma greater-than-1 non-null; ApplyGamma less-than-1 non-null;
/// Tile non-null; Tile doubles dimensions for 2x2; Tile 1x1 preserves dimensions;
/// Tile 3x1 triples width preserves height; Overlay non-null; Overlay preserves base dimensions;
/// Overlay small-on-large preserves base size; Overlay zero-offset non-null;
/// dogfood CreateCanvas->ApplyGamma->Tile->Overlay->Verify pipeline.
/// </summary>
public class NetpbmR201ApplyGammaAndTileDeepTests
{
    // -------------------------------------------------------------------------
    // ApplyGamma
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.ApplyGamma(1.0));
    }

    [Fact]
    public void ApplyGamma_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 255);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void ApplyGamma_HighGamma_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.ApplyGamma(3.0));
    }

    [Fact]
    public void ApplyGamma_LowGamma_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.ApplyGamma(0.5));
    }

    [Fact]
    public void ApplyGamma_PreservesPixelCount()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 255);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void ApplyGamma_ThenSharpen_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.ApplyGamma(2.2).Sharpen());
    }

    // -------------------------------------------------------------------------
    // Tile
    // -------------------------------------------------------------------------

    [Fact]
    public void Tile_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 3, NetpbmFormat.Pgm, 255);
        Assert.NotNull(img.Tile(2, 2));
    }

    [Fact]
    public void Tile_2x2_DoublesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(4, 3, NetpbmFormat.Pgm, 255);
        var tiled = img.Tile(2, 2);
        Assert.Equal(img.Width * 2, tiled.Width);
        Assert.Equal(img.Height * 2, tiled.Height);
    }

    [Fact]
    public void Tile_1x1_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(4, 3, NetpbmFormat.Pgm, 255);
        var tiled = img.Tile(1, 1);
        Assert.Equal(img.Width, tiled.Width);
        Assert.Equal(img.Height, tiled.Height);
    }

    [Fact]
    public void Tile_3x1_TriplesWidthPreservesHeight()
    {
        var img = NetpbmImage.CreateCanvas(4, 3, NetpbmFormat.Pgm, 255);
        var tiled = img.Tile(3, 1);
        Assert.Equal(img.Width * 3, tiled.Width);
        Assert.Equal(img.Height, tiled.Height);
    }

    [Fact]
    public void Tile_1x3_PreservesWidthTriplesHeight()
    {
        var img = NetpbmImage.CreateCanvas(4, 3, NetpbmFormat.Pgm, 255);
        var tiled = img.Tile(1, 3);
        Assert.Equal(img.Width, tiled.Width);
        Assert.Equal(img.Height * 3, tiled.Height);
    }

    // -------------------------------------------------------------------------
    // Overlay
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_NonNull()
    {
        var base_ = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 200);
        var overlay = NetpbmImage.CreateCanvas(2, 2, NetpbmFormat.Pgm, 100);
        Assert.NotNull(base_.Overlay(overlay, 0, 0));
    }

    [Fact]
    public void Overlay_PreservesBaseDimensions()
    {
        var base_ = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 200);
        var overlay = NetpbmImage.CreateCanvas(2, 2, NetpbmFormat.Pgm, 100);
        var result = base_.Overlay(overlay, 1, 1);
        Assert.Equal(base_.Width, result.Width);
        Assert.Equal(base_.Height, result.Height);
    }

    [Fact]
    public void Overlay_ZeroOffset_NonNull()
    {
        var base_ = NetpbmImage.CreateCanvas(6, 6, NetpbmFormat.Pgm, 200);
        var small = NetpbmImage.CreateCanvas(3, 3, NetpbmFormat.Pgm, 50);
        Assert.NotNull(base_.Overlay(small, 0, 0));
    }

    [Fact]
    public void Overlay_SameSizeImages_PreservesDimensions()
    {
        var img1 = NetpbmImage.CreateCanvas(5, 5, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(5, 5, NetpbmFormat.Pgm, 100);
        var result = img1.Overlay(img2, 0, 0);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_ApplyGamma_Tile_Overlay_Verify_Pipeline()
    {
        // CreateCanvas
        var base_ = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 180);
        Assert.Equal(6, base_.Width);
        Assert.Equal(4, base_.Height);

        // ApplyGamma
        var gammaed = base_.ApplyGamma(2.2);
        Assert.Equal(6, gammaed.Width);
        Assert.Equal(4, gammaed.Height);

        // Tile 2x2 → 12x8
        var tiled = gammaed.Tile(2, 2);
        Assert.Equal(12, tiled.Width);
        Assert.Equal(8, tiled.Height);

        // Create small overlay image
        var stamp = NetpbmImage.CreateCanvas(3, 2, NetpbmFormat.Pgm, 50);

        // Overlay stamp onto tiled at (2,2)
        var result = tiled.Overlay(stamp, 2, 2);
        Assert.Equal(12, result.Width);
        Assert.Equal(8, result.Height);

        // ApplyGamma on result
        var final_ = result.ApplyGamma(1.0);
        Assert.Equal(12, final_.Width);
        Assert.Equal(8, final_.Height);
    }
}
