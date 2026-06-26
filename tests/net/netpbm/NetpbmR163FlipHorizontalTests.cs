// Tests for NetpbmImage.FlipHorizontal dedicated coverage.
// Sprint: ff-sprint-s167-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R163

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R163: Dedicated tests for NetpbmImage.FlipHorizontal().
/// FlipHorizontal mirrors the image left-right IN PLACE (modifies the original, void return).
/// Dimensions are preserved. Pixel at (r, c) swaps with pixel at (r, W-1-c).
/// Covers: width unchanged after flip; height unchanged after flip;
/// format unchanged after flip; pixel at column 0 maps to column W-1 after flip;
/// pixel at column W-1 maps to column 0 after flip; center column unchanged (odd width);
/// double flip restores original pixels;
/// dogfood Create->SetPixel->FlipHorizontal->GetPixel;
/// dogfood multi-row flip consistency; dogfood zero-value pixel unaffected.
/// </summary>
public class NetpbmR163FlipHorizontalTests
{
    // -------------------------------------------------------------------------
    // Dimension/format preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipHorizontal();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void FlipHorizontal_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipHorizontal();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void FlipHorizontal_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.FlipHorizontal();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    // -------------------------------------------------------------------------
    // Pixel transform tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_LeftmostPixel_MovesToRightmost()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5); // 4w
        img.SetPixel(0, 0, 99); // row=0, col=0 (leftmost)
        img.FlipHorizontal();
        Assert.Equal(99, img.GetPixel(0, 3)); // now at col=W-1=3
    }

    [Fact]
    public void FlipHorizontal_RightmostPixel_MovesToLeftmost()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 3, 77); // row=0, col=3 (rightmost)
        img.FlipHorizontal();
        Assert.Equal(77, img.GetPixel(0, 0)); // now at col=0
    }

    [Fact]
    public void FlipHorizontal_CenterColumn_OddWidth_Unchanged()
    {
        var img = NetpbmImage.Create(5, 1, NetpbmFormat.PGM_P5); // 5w, center at col=2
        img.SetPixel(0, 2, 55);
        img.FlipHorizontal();
        Assert.Equal(55, img.GetPixel(0, 2)); // center stays
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DoubleFlip_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 1, 88);
        img.FlipHorizontal();
        img.FlipHorizontal(); // flip back
        Assert.Equal(88, img.GetPixel(0, 1));
    }

    [Fact]
    public void DogfoodPipeline_CreateSetPixelFlip_GetPixel()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5); // 3w 2h
        img.SetPixel(1, 0, 42); // row=1, col=0 → after flip at col=2
        img.FlipHorizontal();
        Assert.Equal(42, img.GetPixel(1, 2)); // W-1-0=2
    }

    [Fact]
    public void DogfoodPipeline_MultiRowFlipConsistency()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 0, 20);
        img.SetPixel(2, 0, 30);
        img.FlipHorizontal();
        // All leftmost pixels should now be at col=3 (W-1)
        Assert.Equal(10, img.GetPixel(0, 3));
        Assert.Equal(20, img.GetPixel(1, 3));
        Assert.Equal(30, img.GetPixel(2, 3));
    }

    [Fact]
    public void DogfoodPipeline_ZeroValuePixel_UnaffectedByFlip()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        // All pixels are 0 by default; flip should keep them 0
        img.FlipHorizontal();
        Assert.Equal(0, img.GetPixel(0, 0));
        Assert.Equal(0, img.GetPixel(0, 3));
    }
}
