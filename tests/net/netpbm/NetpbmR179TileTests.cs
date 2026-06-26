// Tests for NetpbmImage.Tile dedicated coverage.
// Sprint: ff-sprint-s183-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R179

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R179: Dedicated tests for NetpbmImage.Tile(int tilesX, int tilesY).
/// Creates a tiled image by repeating this image in a tilesX-by-tilesY grid.
/// tilesX &lt; 1 throws ArgumentOutOfRangeException.
/// tilesY &lt; 1 throws ArgumentOutOfRangeException.
/// Result width = Width * tilesX; Result height = Height * tilesY.
/// Format and MaxValue are preserved.
/// Returns a new image (not same reference).
/// Covers: tilesX=0 throws; tilesX negative throws; tilesY=0 throws;
/// tilesY negative throws; result width=Width*tilesX; result height=Height*tilesY;
/// returns new image; format preserved; MaxValue preserved; 1x1 tile is clone;
/// dogfood 2x3 tiling dims correct.
/// </summary>
public class NetpbmR179TileTests
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
    public void Tile_NegativeTilesX_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(-1, 2));
    }

    [Fact]
    public void Tile_ZeroTilesY_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(2, 0));
    }

    [Fact]
    public void Tile_NegativeTilesY_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Tile(2, -1));
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Tile_ResultWidth_EqualsWidthTimestilesX()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5);
        var result = img.Tile(4, 2);
        Assert.Equal(3 * 4, result.Width);
    }

    [Fact]
    public void Tile_ResultHeight_EqualsHeightTimestilesY()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5);
        var result = img.Tile(4, 2);
        Assert.Equal(5 * 2, result.Height);
    }

    [Fact]
    public void Tile_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Tile(2, 2);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Tile_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Tile(2, 2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Tile_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Tile(2, 2);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Tile_OneByOne_SameDimensions()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var result = img.Tile(1, 1);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoByThree_DimsCorrect()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        var result = img.Tile(2, 3);
        Assert.Equal(5 * 2, result.Width);
        Assert.Equal(3 * 3, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }
}
