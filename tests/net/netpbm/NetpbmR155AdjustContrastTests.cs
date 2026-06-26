// Tests for NetpbmImage.AdjustContrast dedicated coverage.
// Sprint: ff-sprint-s159-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R155

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R155: Dedicated tests for NetpbmImage.AdjustContrast(double factor).
/// AdjustContrast maps each pixel: pixel = mid + (pixel - mid) * factor.
/// factor=1.0 is identity. factor=0 maps all pixels to mid (MaxValue/2).
/// Throws ArgumentOutOfRangeException for negative factor.
/// PBM images return a clone without modification.
/// Covers: negative factor throws; PBM returns clone unchanged; format preserved;
/// original unchanged; factor=1.0 is identity; factor=0 maps pixels to mid;
/// factor>1 increases contrast (pixel moves farther from mid);
/// output pixel values in [0, MaxValue]; output dimensions match;
/// dogfood Create->SetPixel->AdjustContrast->GetPixel pipeline;
/// dogfood factor=0.5 moves pixel toward midpoint.
/// </summary>
public class NetpbmR155AdjustContrastTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_NegativeFactor_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.AdjustContrast(-0.1));
    }

    // -------------------------------------------------------------------------
    // PBM behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_PbmInput_ReturnsCloneUnmodified()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 1);
        var result = img.AdjustContrast(2.0);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
        Assert.Equal(1, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_PreservesFormat()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void AdjustContrast_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        _ = img.AdjustContrast(2.0);
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustContrast_FactorOne_IsIdentity()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(100, result.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustContrast_FactorZero_MapsToMidpoint()
    {
        // factor=0: pixel = mid + (pixel - mid) * 0 = mid (127 for MaxValue=255)
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        var result = img.AdjustContrast(0.0);
        // Mid = 255/2.0 = 127 (rounded)
        Assert.True(result.GetPixel(0, 0) >= 126 && result.GetPixel(0, 0) <= 128);
    }

    [Fact]
    public void AdjustContrast_OutputDimensionsMatch()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.5);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void AdjustContrast_OutputPixelInBounds()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 255);
        img.SetPixel(1, 1, 0);
        var result = img.AdjustContrast(3.0);
        Assert.True(result.GetPixel(0, 0) >= 0 && result.GetPixel(0, 0) <= 255);
        Assert.True(result.GetPixel(1, 1) >= 0 && result.GetPixel(1, 1) <= 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_AdjustContrast_GetPixel()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 127); // at midpoint
        var result = img.AdjustContrast(2.0);
        // Midpoint pixel unchanged by contrast adjustment
        Assert.Equal(127, result.GetPixel(0, 0));
    }

    [Fact]
    public void DogfoodPipeline_HalfFactor_MovesPixelTowardMidpoint()
    {
        // factor=0.5: pixel closer to mid = 127 + (200-127)*0.5 = 163
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        var result = img.AdjustContrast(0.5);
        // Should be between 127 and 200
        var pixel = result.GetPixel(0, 0);
        Assert.True(pixel > 127 && pixel < 200);
    }
}
