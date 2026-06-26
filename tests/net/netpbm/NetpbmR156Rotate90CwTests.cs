// Tests for NetpbmImage.Rotate90Cw dedicated coverage.
// Sprint: ff-sprint-s160-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R156

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R156: Dedicated tests for NetpbmImage.Rotate90Cw().
/// Rotate90Cw returns a NEW image rotated 90 degrees clockwise.
/// Output Width equals input Height; output Height equals input Width.
/// Pixel at (r, c) in source maps to (c, Height-1-r) in result.
/// Covers: output Width equals source Height; output Height equals source Width;
/// square image dims unchanged; format preserved; original unchanged after rotate;
/// top-left pixel maps correctly; arbitrary pixel maps correctly;
/// dogfood Create->SetPixel->Rotate90Cw->GetPixel; four rotations restores original dims;
/// dogfood non-square full pixel transform.
/// </summary>
public class NetpbmR156Rotate90CwTests
{
    // -------------------------------------------------------------------------
    // Dimension tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90Cw_OutputWidth_EqualsSourceHeight()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4 wide, 3 tall
        var result = img.Rotate90Cw();
        Assert.Equal(3, result.Width); // output width = source height
    }

    [Fact]
    public void Rotate90Cw_OutputHeight_EqualsSourceWidth()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4 wide, 3 tall
        var result = img.Rotate90Cw();
        Assert.Equal(4, result.Height); // output height = source width
    }

    [Fact]
    public void Rotate90Cw_SquareImage_DimsUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Rotate90Cw();
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90Cw_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var result = img.Rotate90Cw();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Rotate90Cw_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        _ = img.Rotate90Cw();
        Assert.Equal(4, img.Width);
        Assert.Equal(3, img.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel transform tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90Cw_TopLeftPixel_MapsToTopRight()
    {
        // In a 90CW rotation, source (0,0) → dest (0, Height-1) i.e. top-right of dest
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4w 3h
        img.SetPixel(0, 0, 99); // row=0, col=0
        var result = img.Rotate90Cw(); // 3w 4h
        // dstRow=col=0, dstCol=Height-1-r=3-1-0=2 → result pixel at (0,2)
        Assert.Equal(99, result.GetPixel(0, 2));
    }

    [Fact]
    public void Rotate90Cw_ArbitraryPixel_MapsCorrectly()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5); // 5w 4h
        img.SetPixel(1, 2, 77); // row=1, col=2
        var result = img.Rotate90Cw(); // 4w 5h
        // dstRow=col=2, dstCol=Height-1-r=4-1-1=2 → result pixel at (2,2)
        Assert.Equal(77, result.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateSetPixelRotate_GetPixel()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5); // 3w 2h
        img.SetPixel(0, 0, 50);  // row=0, col=0
        img.SetPixel(1, 2, 200); // row=1, col=2
        var result = img.Rotate90Cw(); // 2w 3h
        // row=0,col=0 → dstRow=0, dstCol=2-1-0=1
        Assert.Equal(50, result.GetPixel(0, 1));
        // row=1,col=2 → dstRow=2, dstCol=2-1-1=0
        Assert.Equal(200, result.GetPixel(2, 0));
    }

    [Fact]
    public void DogfoodPipeline_FourRotations_RestoresDims()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5);
        var r1 = img.Rotate90Cw();
        var r2 = r1.Rotate90Cw();
        var r3 = r2.Rotate90Cw();
        var r4 = r3.Rotate90Cw();
        Assert.Equal(img.Width, r4.Width);
        Assert.Equal(img.Height, r4.Height);
    }

    [Fact]
    public void DogfoodPipeline_NonSquare_FullPixelTransform()
    {
        var img = NetpbmImage.Create(2, 3, NetpbmFormat.PGM_P5); // 2w 3h
        img.SetPixel(2, 1, 111); // row=2, col=1
        var result = img.Rotate90Cw(); // 3w 2h
        // dstRow=col=1, dstCol=Height-1-r=3-1-2=0 → result pixel at (1,0)
        Assert.Equal(111, result.GetPixel(1, 0));
    }
}
