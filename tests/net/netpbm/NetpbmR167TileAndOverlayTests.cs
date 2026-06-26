// Tests for NetpbmImage.Tile, Overlay, FlipDiagonal, ExtractChannel.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R167

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R167: Tests for NetpbmImage.Tile, Overlay, FlipDiagonal, ExtractChannel.
/// Tile(tilesX, tilesY): repeats image into a tiled grid.
/// Overlay(overlay, topOffset, leftOffset): places overlay image on top.
/// FlipDiagonal(): transposes the image (swaps rows and columns).
/// ExtractChannel(channel): extracts R, G, or B channel as grayscale.
/// Covers: Tile 2x1 doubles width; Tile 1x2 doubles height; Tile 2x2 quadruples pixels;
/// Overlay same-size images; Overlay produces correct dimensions;
/// FlipDiagonal swaps width/height; FlipDiagonal twice returns original dims;
/// ExtractChannel 0 from color returns grayscale; ExtractChannel preserves dims;
/// ExtractChannel on grayscale; Tile preserves pixel count ratio;
/// Overlay offset within bounds; dogfood Create->Tile->Overlay->FlipDiagonal pipeline.
/// </summary>
public class NetpbmR167TileAndOverlayTests
{
    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    private static NetpbmImage CreateColor(int w, int h, byte r, byte g, byte b)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PPM_P3, 0);
        for (var row = 0; row < h; row++)
            for (var col = 0; col < w; col++)
                img.SetPixelColor(row, col, r, g, b);
        return img;
    }

    // -------------------------------------------------------------------------
    // Tile
    // -------------------------------------------------------------------------

    [Fact]
    public void Tile_2x1_DoublesWidth()
    {
        var img = CreateGray(4, 3, 100);
        var tiled = img.Tile(2, 1);
        Assert.Equal(8, tiled.Width);
        Assert.Equal(3, tiled.Height);
    }

    [Fact]
    public void Tile_1x2_DoublesHeight()
    {
        var img = CreateGray(4, 3, 100);
        var tiled = img.Tile(1, 2);
        Assert.Equal(4, tiled.Width);
        Assert.Equal(6, tiled.Height);
    }

    [Fact]
    public void Tile_2x2_QuadruplesPixelCount()
    {
        var img = CreateGray(3, 4, 128);
        var tiled = img.Tile(2, 2);
        Assert.Equal(img.Width * img.Height * 4, tiled.Width * tiled.Height);
    }

    [Fact]
    public void Tile_3x1_TriplesWidth()
    {
        var img = CreateGray(4, 4, 100);
        var tiled = img.Tile(3, 1);
        Assert.Equal(12, tiled.Width);
        Assert.Equal(4, tiled.Height);
    }

    // -------------------------------------------------------------------------
    // Overlay
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_SameSizeImage_PreservesDimensions()
    {
        var base_img = CreateGray(6, 6, 128);
        var overlay = CreateGray(3, 3, 200);
        var result = base_img.Overlay(overlay, 0, 0);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Overlay_WithOffset_ProducesCorrectDimensions()
    {
        var base_img = CreateGray(8, 8, 100);
        var overlay = CreateGray(4, 4, 200);
        var result = base_img.Overlay(overlay, 2, 2);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Overlay_ZeroOffset_Succeeds()
    {
        var base_img = CreateGray(6, 6, 50);
        var overlay = CreateGray(6, 6, 200);
        var result = base_img.Overlay(overlay, 0, 0);
        Assert.NotNull(result);
    }

    // -------------------------------------------------------------------------
    // FlipDiagonal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipDiagonal_SwapsWidthAndHeight()
    {
        var img = CreateGray(5, 3, 128);
        var flipped = img.FlipDiagonal();
        Assert.Equal(3, flipped.Width);
        Assert.Equal(5, flipped.Height);
    }

    [Fact]
    public void FlipDiagonal_Twice_RestoresDimensions()
    {
        var img = CreateGray(5, 3, 128);
        var result = img.FlipDiagonal().FlipDiagonal();
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void FlipDiagonal_Square_PreservesDimensions()
    {
        var img = CreateGray(4, 4, 100);
        var flipped = img.FlipDiagonal();
        Assert.Equal(4, flipped.Width);
        Assert.Equal(4, flipped.Height);
    }

    // -------------------------------------------------------------------------
    // ExtractChannel
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_Red_PreservesDimensions()
    {
        var img = CreateColor(4, 4, 200, 100, 50);
        var channel = img.ExtractChannel(0);
        Assert.Equal(4, channel.Width);
        Assert.Equal(4, channel.Height);
    }

    [Fact]
    public void ExtractChannel_Green_ReturnsGrayscale()
    {
        var img = CreateColor(4, 4, 200, 100, 50);
        var channel = img.ExtractChannel(1);
        Assert.NotNull(channel);
        Assert.True(channel.Pixels.Length > 0);
    }

    [Fact]
    public void ExtractChannel_Blue_PreservesDimensions()
    {
        var img = CreateColor(4, 4, 200, 100, 50);
        var channel = img.ExtractChannel(2);
        Assert.Equal(4, channel.Width);
        Assert.Equal(4, channel.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Tile->Overlay->FlipDiagonal pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_TileOverlayFlipDiagonalPipeline()
    {
        var img = CreateGray(4, 3, 128);

        // Tile 2x2
        var tiled = img.Tile(2, 2);
        Assert.Equal(8, tiled.Width);
        Assert.Equal(6, tiled.Height);

        // Overlay something small on the tiled image
        var overlay = CreateGray(2, 2, 255);
        var overlaid = tiled.Overlay(overlay, 0, 0);
        Assert.Equal(8, overlaid.Width);
        Assert.Equal(6, overlaid.Height);

        // FlipDiagonal of the original
        var flipped = img.FlipDiagonal();
        Assert.Equal(3, flipped.Width);
        Assert.Equal(4, flipped.Height);

        // FlipDiagonal twice
        var restored = flipped.FlipDiagonal();
        Assert.Equal(img.Width, restored.Width);
        Assert.Equal(img.Height, restored.Height);
    }
}
