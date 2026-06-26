// Tests for NetpbmImage.Tile dedicated coverage.
// Sprint: ff-sprint-s152-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R148

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R148: Dedicated tests for NetpbmImage.Tile(int tilesX, int tilesY).
/// Tile returns a new image tiling the source tilesX times horizontally and tilesY times vertically.
/// Throws ArgumentOutOfRangeException if tilesX or tilesY is less than 1.
/// Output dimensions = Width*tilesX by Height*tilesY.
/// Covers: zero tilesX throws; zero tilesY throws; negative tilesX throws; negative tilesY throws;
/// output width is Width*tilesX; output height is Height*tilesY; format preserved;
/// original unchanged after tile; 1x1 tile returns same dimensions;
/// dogfood Create->SetPixel->Tile->GetPixel verifies pixel replication;
/// dogfood 2x2 tile quadruples pixel count.
/// </summary>
public class NetpbmR148TileTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Tile_ZeroTilesX_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(0, 2));
    }

    [Fact]
    public void Tile_ZeroTilesY_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(2, 0));
    }

    [Fact]
    public void Tile_NegativeTilesX_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(-1, 2));
    }

    [Fact]
    public void Tile_NegativeTilesY_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(2, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Tile_OutputWidth_IsWidthTimestilesX()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var tiled = img.Tile(4, 1);
        Assert.Equal(12, tiled.Width); // 3 * 4
    }

    [Fact]
    public void Tile_OutputHeight_IsHeightTimestilesY()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var tiled = img.Tile(1, 3);
        Assert.Equal(6, tiled.Height); // 2 * 3
    }

    [Fact]
    public void Tile_PreservesFormat()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var tiled = img.Tile(2, 2);
        Assert.Equal(NetpbmFormat.PGM_P5, tiled.Format);
    }

    [Fact]
    public void Tile_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 44);
        _ = img.Tile(3, 3);
        Assert.Equal(2, img.Width);
        Assert.Equal(2, img.Height);
        Assert.Equal(44, img.GetPixel(0, 0));
    }

    [Fact]
    public void Tile_OneByOne_ReturnsSameDimensions()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var tiled = img.Tile(1, 1);
        Assert.Equal(5, tiled.Width);
        Assert.Equal(3, tiled.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_Tile_GetPixel()
    {
        // 2x2 image: top-left pixel = 100
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);

        // Tile 2x2 → 4x4 image; top-left of each tile copy should be 100
        var tiled = img.Tile(2, 2);
        Assert.Equal(100, tiled.GetPixel(0, 0)); // top-left of first tile
        Assert.Equal(100, tiled.GetPixel(0, 2)); // top-left of second tile (right)
        Assert.Equal(100, tiled.GetPixel(2, 0)); // top-left of third tile (below)
    }

    [Fact]
    public void DogfoodPipeline_TwoByTwo_Tile_QuadruplesArea()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var tiled = img.Tile(2, 2);
        Assert.Equal(6, tiled.Width);   // 3 * 2
        Assert.Equal(8, tiled.Height);  // 4 * 2
    }
}
