// Tests for NetpbmImage.ApplyGamma dedicated coverage.
// Sprint: ff-sprint-s172-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R168

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R168: Dedicated tests for NetpbmImage.ApplyGamma(double gamma).
/// Applies gamma correction: output = max * (input/max)^gamma, clamped to [0,MaxValue].
/// Returns a NEW image. PBM images return an unchanged clone.
/// Throws ArgumentOutOfRangeException if gamma is zero or negative.
/// gamma=1.0 is the identity (pixel values unchanged).
/// Covers: gamma=0 throws; negative gamma throws; PBM returns clone;
/// returns NEW image; width unchanged; height unchanged; format unchanged;
/// original unchanged after apply; gamma=1.0 identity for PGM;
/// dogfood single-pixel gamma=1.0 preserves value; all-zero image stays zero.
/// </summary>
public class NetpbmR168ApplyGammaTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_ZeroGamma_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(0.0));
    }

    [Fact]
    public void ApplyGamma_NegativeGamma_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(-1.5));
    }

    // -------------------------------------------------------------------------
    // Format-specific behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_PbmFormat_ReturnsCloneWithSameFormat()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P4);
        var result = img.ApplyGamma(2.0);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
    }

    // -------------------------------------------------------------------------
    // Return value and structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(1.0);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ApplyGamma_Width_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void ApplyGamma_Height_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void ApplyGamma_Format_Unchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void ApplyGamma_Original_UnchangedAfterApply()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 200);
        img.ApplyGamma(2.0);
        Assert.Equal(200, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GammaOne_IsIdentity()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 128);
        var result = img.ApplyGamma(1.0);
        // gamma=1.0: output = max*(input/max)^1 = input
        Assert.Equal(128, result.GetPixel(1, 1));
    }

    [Fact]
    public void DogfoodPipeline_AllZeroImage_StaysZeroAfterGamma()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5); // all zeros
        var result = img.ApplyGamma(2.2);
        // 0^gamma = 0 for any positive gamma
        Assert.Equal(0, result.GetPixel(0, 0));
    }
}
