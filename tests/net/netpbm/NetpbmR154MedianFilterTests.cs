// Tests for NetpbmImage.MedianFilter dedicated coverage.
// Sprint: ff-sprint-s158-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R154

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R154: Dedicated tests for NetpbmImage.MedianFilter(int radius).
/// MedianFilter applies a median smoothing filter with the given radius.
/// Radius=0 returns a clone (identity). Negative radius throws ArgumentOutOfRangeException.
/// Covers: negative radius throws ArgumentOutOfRangeException; radius=0 returns clone;
/// format preserved; original unchanged; output dimensions match;
/// uniform image interior unchanged by median filter; PBM format preserved;
/// result is a new object (non-destructive); output pixel values in [0, MaxValue];
/// dogfood Create->SetPixel->MedianFilter->GetPixel output bounds;
/// dogfood radius=1 on small image does not throw.
/// </summary>
public class NetpbmR154MedianFilterTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_NegativeRadius_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.MedianFilter(-1));
    }

    // -------------------------------------------------------------------------
    // Radius=0 identity
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_RadiusZero_ReturnsClone()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 77);
        var result = img.MedianFilter(0);
        Assert.Equal(77, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_PreservesFormat()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MedianFilter_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 2, 150);
        _ = img.MedianFilter(1);
        Assert.Equal(150, img.GetPixel(2, 2));
    }

    [Fact]
    public void MedianFilter_OutputDimensionsMatchInput()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void MedianFilter_UniformImage_PixelUnchanged()
    {
        // All pixels = 100; median is 100
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, 100);
        var result = img.MedianFilter(1);
        Assert.Equal(100, result.GetPixel(2, 2)); // center pixel unchanged
    }

    [Fact]
    public void MedianFilter_PbmFormat_PreservesFormat()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P1);
        var result = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    [Fact]
    public void MedianFilter_ResultIsNewObject_NonDestructive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.NotSame(img, result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_MedianFilter_OutputInBounds()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0);
        img.SetPixel(4, 4, 255);
        img.SetPixel(2, 2, 128);
        var result = img.MedianFilter(1);
        // All output pixels should be in [0, 255]
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                Assert.True(result.GetPixel(r, c) >= 0 && result.GetPixel(r, c) <= 255);
    }

    [Fact]
    public void DogfoodPipeline_Radius1_SmallImage_DoesNotThrow()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 99);
        var result = img.MedianFilter(1);
        Assert.Equal(3, result.Width);
        Assert.Equal(3, result.Height);
    }
}
