// Tests for NetpbmImage.BlurBox dedicated coverage.
// Sprint: ff-sprint-s169-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R165

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R165: Dedicated tests for NetpbmImage.BlurBox(int radius).
/// BlurBox applies a box blur (averaging filter) over a square neighborhood.
/// Returns a NEW image. PBM images return an unchanged clone (no averaging).
/// Throws ArgumentOutOfRangeException if radius is less than 1.
/// Covers: radius-zero throws; radius-negative throws; PBM returns clone;
/// returns NEW image; Width unchanged; Height unchanged; Format unchanged;
/// original unchanged after blur; radius=1 produces valid result;
/// dogfood Create->SetPixel->Blur->GetPixel; uniform image unchanged by blur.
/// </summary>
public class NetpbmR165BlurBoxTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_RadiusZero_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.BlurBox(0));
    }

    [Fact]
    public void BlurBox_NegativeRadius_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.BlurBox(-1));
    }

    // -------------------------------------------------------------------------
    // Format-specific behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_PbmFormat_ReturnsCloneWithSameDims()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.BlurBox(1);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
    }

    // -------------------------------------------------------------------------
    // Return value and structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurBox_Width_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void BlurBox_Height_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void BlurBox_Format_Unchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void BlurBox_Original_UnchangedAfterBlur()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        img.BlurBox(1);
        // Original should still have 200 at (0,0)
        Assert.Equal(200, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_BlurProducesUniformResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        // Set all pixels to same value
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, 100);
        var result = img.BlurBox(1);
        // Averaging identical values produces the same value
        Assert.Equal(100, result.GetPixel(1, 1));
    }

    [Fact]
    public void DogfoodPipeline_CreateSetPixelBlur_ResultInBounds()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 255); // center pixel max value
        var result = img.BlurBox(1);
        // Result pixel at center is average of neighbors — must be in [0,255]
        var px = result.GetPixel(1, 1);
        Assert.InRange(px, 0, 255);
    }
}
