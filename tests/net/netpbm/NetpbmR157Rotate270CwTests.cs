// Tests for NetpbmImage.Rotate270Cw dedicated coverage.
// Sprint: ff-sprint-s161-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R157

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R157: Dedicated tests for NetpbmImage.Rotate270Cw().
/// Rotate270Cw returns a NEW image rotated 270° clockwise (90° counter-clockwise).
/// Output Width equals input Height; output Height equals input Width.
/// Pixel at (r, c) in source maps to (W-1-c, r) in result.
/// Covers: output Width equals source Height; output Height equals source Width;
/// square image dims unchanged; format preserved; original unchanged after rotate;
/// pixel (r,c) maps to (W-1-c, r); top-right maps to top-left;
/// dogfood Create->SetPixel->Rotate270Cw->GetPixel; four rotations restores original dims;
/// dogfood non-square full pixel transform.
/// </summary>
public class NetpbmR157Rotate270CwTests
{
    // -------------------------------------------------------------------------
    // Dimension tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270Cw_OutputWidth_EqualsSourceHeight()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4 wide, 3 tall
        var result = img.Rotate270Cw();
        Assert.Equal(3, result.Width); // output width = source height
    }

    [Fact]
    public void Rotate270Cw_OutputHeight_EqualsSourceWidth()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4 wide, 3 tall
        var result = img.Rotate270Cw();
        Assert.Equal(4, result.Height); // output height = source width
    }

    [Fact]
    public void Rotate270Cw_SquareImage_DimsUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270Cw_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var result = img.Rotate270Cw();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Rotate270Cw_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        _ = img.Rotate270Cw();
        Assert.Equal(4, img.Width);
        Assert.Equal(3, img.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel transform tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate270Cw_ArbitraryPixel_MapsToWMinus1MinusCAndR()
    {
        // Rotate270Cw: src(r,c) → dst(W-1-c, r)
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5); // 5w 4h
        img.SetPixel(1, 2, 77); // row=1, col=2
        var result = img.Rotate270Cw(); // 4w 5h
        // dstRow=W-1-c=5-1-2=2, dstCol=r=1 → result.GetPixel(2, 1)
        Assert.Equal(77, result.GetPixel(2, 1));
    }

    [Fact]
    public void Rotate270Cw_TopRightPixel_MapsToTopLeft()
    {
        // src(0, W-1) → dst(W-1-(W-1), 0) = dst(0, 0)
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4w 3h
        img.SetPixel(0, 3, 88); // row=0, col=3 (top-right)
        var result = img.Rotate270Cw(); // 3w 4h
        // dstRow=4-1-3=0, dstCol=0 → result.GetPixel(0,0)
        Assert.Equal(88, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateSetPixelRotate_GetPixel()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5); // 3w 2h
        img.SetPixel(0, 1, 50);  // row=0, col=1
        var result = img.Rotate270Cw(); // 2w 3h
        // dstRow=W-1-c=3-1-1=1, dstCol=r=0 → result.GetPixel(1,0)
        Assert.Equal(50, result.GetPixel(1, 0));
    }

    [Fact]
    public void DogfoodPipeline_FourRotations_RestoresDims()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5);
        var r1 = img.Rotate270Cw();
        var r2 = r1.Rotate270Cw();
        var r3 = r2.Rotate270Cw();
        var r4 = r3.Rotate270Cw();
        Assert.Equal(img.Width, r4.Width);
        Assert.Equal(img.Height, r4.Height);
    }

    [Fact]
    public void DogfoodPipeline_NonSquare_PixelAtBottomLeft()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4w 3h
        img.SetPixel(2, 0, 123); // row=2, col=0 (bottom-left)
        var result = img.Rotate270Cw(); // 3w 4h
        // dstRow=W-1-c=4-1-0=3, dstCol=r=2 → result.GetPixel(3,2)
        Assert.Equal(123, result.GetPixel(3, 2));
    }
}
