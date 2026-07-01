// Tests for NetpbmImage.GetGamma dedicated coverage.
// Sprint: ff-sprint-s427-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R445

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R445: Dedicated tests for NetpbmImage.GetGamma().
/// Returns positive value.
/// Width unchanged after GetGamma.
/// Height unchanged after GetGamma.
/// Format unchanged after GetGamma.
/// MaxValue unchanged after GetGamma.
/// Idempotent (called twice same result).
/// PBM gamma positive.
/// PGM gamma positive.
/// PPM gamma positive.
/// Dogfood: 4x4 PGM gamma positive.
/// Dogfood: 4x4 PPM gamma positive.
/// </summary>
public class NetpbmR445GetGammaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGamma_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double gamma = img.GetGamma();
        Assert.True(gamma > 0.0);
    }

    [Fact]
    public void GetGamma_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetGamma();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetGamma_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetGamma();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetGamma_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetGamma();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetGamma_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetGamma();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetGamma_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetGamma();
        double second = img.GetGamma();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetGamma_PBM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetGamma() > 0.0);
    }

    [Fact]
    public void GetGamma_PGM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetGamma() > 0.0);
    }

    [Fact]
    public void GetGamma_PPM_Positive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetGamma() > 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_GammaPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetGamma() > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_GammaPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetGamma() > 0.0);
    }
}
