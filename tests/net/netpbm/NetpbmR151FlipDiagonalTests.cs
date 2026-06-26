// Tests for NetpbmImage.FlipDiagonal dedicated coverage.
// Sprint: ff-sprint-s155-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R151

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R151: Dedicated tests for NetpbmImage.FlipDiagonal().
/// FlipDiagonal transposes the image (swaps rows and columns): pixel[r,c] → pixel[c,r].
/// Output dimensions: Width becomes Height and Height becomes Width.
/// Covers: output width equals original height; output height equals original width;
/// square image dimensions unchanged; format preserved; original unchanged;
/// top-left pixel stays at top-left; pixel at (r,c) maps to (c,r) in result;
/// dogfood Create->SetPixel->FlipDiagonal->GetPixel pixel at known position;
/// dogfood FlipDiagonal->FlipDiagonal returns original dimensions;
/// dogfood non-square: correct transposed pixel access.
/// </summary>
public class NetpbmR151FlipDiagonalTests
{
    // -------------------------------------------------------------------------
    // Dimension tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipDiagonal_OutputWidth_EqualsOriginalHeight()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5); // 3 wide, 5 tall
        var result = img.FlipDiagonal();
        Assert.Equal(5, result.Width); // Height becomes Width
    }

    [Fact]
    public void FlipDiagonal_OutputHeight_EqualsOriginalWidth()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5); // 3 wide, 5 tall
        var result = img.FlipDiagonal();
        Assert.Equal(3, result.Height); // Width becomes Height
    }

    [Fact]
    public void FlipDiagonal_SquareImage_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // Format and mutation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipDiagonal_PreservesFormat()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void FlipDiagonal_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 77);
        _ = img.FlipDiagonal();
        Assert.Equal(3, img.Width);
        Assert.Equal(4, img.Height);
        Assert.Equal(77, img.GetPixel(0, 0));
    }

    [Fact]
    public void FlipDiagonal_TopLeftPixel_StaysAtTopLeft()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 123);
        var result = img.FlipDiagonal();
        Assert.Equal(123, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Pixel mapping test
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipDiagonal_PixelAtRC_MapsToPixelAtCR()
    {
        // 4 wide (cols), 3 tall (rows)
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 2, 99); // row=1, col=2
        var result = img.FlipDiagonal(); // now 3 wide, 4 tall
        Assert.Equal(99, result.GetPixel(2, 1)); // row=2, col=1 (transposed)
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_FlipDiagonal_GetPixel()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5); // 3 wide, 2 tall
        img.SetPixel(0, 2, 88); // row=0, col=2
        var result = img.FlipDiagonal(); // now 2 wide, 3 tall
        Assert.Equal(88, result.GetPixel(2, 0)); // row=2, col=0
    }

    [Fact]
    public void DogfoodPipeline_FlipDiagonal_Twice_RestoresOriginalDimensions()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5);
        var twice = img.FlipDiagonal().FlipDiagonal();
        Assert.Equal(3, twice.Width);
        Assert.Equal(5, twice.Height);
    }

    [Fact]
    public void DogfoodPipeline_NonSquare_TransposedPixelAccess()
    {
        // 2 wide, 3 tall image; set (row=2, col=1) = 55
        var img = NetpbmImage.Create(2, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 1, 55);
        var result = img.FlipDiagonal(); // now 3 wide, 2 tall
        // Should appear at (row=1, col=2)
        Assert.Equal(55, result.GetPixel(1, 2));
    }
}
