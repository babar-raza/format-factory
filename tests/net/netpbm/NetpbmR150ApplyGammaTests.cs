// Tests for NetpbmImage.ApplyGamma dedicated coverage.
// Sprint: ff-sprint-s154-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R150

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R150: Dedicated tests for NetpbmImage.ApplyGamma(double gamma).
/// ApplyGamma applies gamma correction: pixel = MaxValue * (pixel/MaxValue)^gamma.
/// Throws ArgumentOutOfRangeException if gamma is zero or negative.
/// PBM images return a clone without modification.
/// Covers: zero gamma throws; negative gamma throws; PBM returns clone unchanged;
/// gamma=1.0 is identity (pixel unchanged); gamma>1 darkens midtones (pixel < original);
/// gamma<1 brightens midtones (pixel > original); format preserved; original unchanged;
/// dogfood Create->SetPixel->ApplyGamma->GetPixel pipeline;
/// dogfood gamma=2.0 reduces mid-range pixel value.
/// </summary>
public class NetpbmR150ApplyGammaTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_ZeroGamma_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(0.0));
    }

    [Fact]
    public void ApplyGamma_NegativeGamma_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(-1.0));
    }

    // -------------------------------------------------------------------------
    // PBM behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_PbmInput_ReturnsCloneUnmodified()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 1);
        var result = img.ApplyGamma(2.0);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
        Assert.Equal(1, result.GetPixel(0, 0)); // unchanged
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_GammaOne_IsIdentity()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(128, result.GetPixel(0, 0));
    }

    [Fact]
    public void ApplyGamma_GammaAboveOne_DarkensMidtones()
    {
        // gamma > 1 darkens: (128/255)^2 * 255 ≈ 64
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.ApplyGamma(2.0);
        Assert.True(result.GetPixel(0, 0) < 128);
    }

    [Fact]
    public void ApplyGamma_GammaBelowOne_BrightensMidtones()
    {
        // gamma < 1 brightens: (128/255)^0.5 * 255 ≈ 181
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.ApplyGamma(0.5);
        Assert.True(result.GetPixel(0, 0) > 128);
    }

    [Fact]
    public void ApplyGamma_PreservesFormat()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(1.5);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void ApplyGamma_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        _ = img.ApplyGamma(2.0);
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_ApplyGamma_GetPixel()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 255); // max value — unaffected by any gamma
        img.SetPixel(1, 1, 0);   // zero value — unaffected by any gamma

        var result = img.ApplyGamma(2.0);
        Assert.Equal(255, result.GetPixel(0, 0)); // max stays max
        Assert.Equal(0, result.GetPixel(1, 1));   // zero stays zero
    }

    [Fact]
    public void DogfoodPipeline_Gamma2_ReducesMidRangePixel()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        var result = img.ApplyGamma(2.0);
        // (200/255)^2 * 255 ≈ 157
        var pixel = result.GetPixel(0, 0);
        Assert.True(pixel >= 150 && pixel <= 165);
    }
}
