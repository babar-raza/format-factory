// Tests for NetpbmImage.FlipDiagonal dedicated coverage.
// Sprint: ff-sprint-s184-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R180

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R180: Dedicated tests for NetpbmImage.FlipDiagonal().
/// Transposes the image along the main diagonal: (x,y) → (y,x).
/// Width and Height are swapped in the result.
/// Format and MaxValue are preserved.
/// Returns a new image (not same reference).
/// Double-flip restores original dimensions.
/// Covers: returns new image; result width equals original Height;
/// result height equals original Width; format preserved; MaxValue preserved;
/// square image same width and height; non-square dims swap;
/// double-flip restores dims; pixel at (r,c) maps to (c,r) in result;
/// dogfood PGM transpose dims; dogfood non-square transpose.
/// </summary>
public class NetpbmR180FlipDiagonalTests
{
    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipDiagonal_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void FlipDiagonal_ResultWidth_EqualsOriginalHeight()
    {
        var img = NetpbmImage.Create(3, 7, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(7, result.Width);
    }

    [Fact]
    public void FlipDiagonal_ResultHeight_EqualsOriginalWidth()
    {
        var img = NetpbmImage.Create(3, 7, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void FlipDiagonal_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void FlipDiagonal_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void FlipDiagonal_SquareImage_SameDimensions()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void FlipDiagonal_NonSquare_DimensionsSwapped()
    {
        var img = NetpbmImage.Create(6, 2, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal();
        Assert.Equal(2, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void FlipDiagonal_DoubleFip_RestoresDimensions()
    {
        var img = NetpbmImage.Create(3, 8, NetpbmFormat.PGM_P5);
        var result = img.FlipDiagonal().FlipDiagonal();
        Assert.Equal(3, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void FlipDiagonal_PixelMapping_RowColSwapped()
    {
        // Pixel at (row=1, col=0) in 3-wide x 5-tall image
        // should appear at (row=0, col=1) in the transposed image
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 0, 200); // row=1, col=0
        var result = img.FlipDiagonal();
        // In result: Width=5, Height=3. The pixel moves to row=0,col=1
        Assert.Equal(200, result.GetPixel(0, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmTranspose_DimsSwapped()
    {
        var img = NetpbmImage.Create(10, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.FlipDiagonal();
        Assert.Equal(4, result.Width);
        Assert.Equal(10, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }
}
