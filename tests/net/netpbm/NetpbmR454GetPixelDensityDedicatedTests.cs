// Tests for NetpbmImage.GetPixelDensity dedicated coverage.
// Sprint: ff-sprint-s436-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R454

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R454: Dedicated tests for NetpbmImage.GetPixelDensity().
/// Returns positive value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM pixel density positive.
/// </summary>
public class NetpbmR454GetPixelDensityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelDensity_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetPixelDensity();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetPixelDensity_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelDensity_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelDensity_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelDensity_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelDensity_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetPixelDensity();
        double second = img.GetPixelDensity();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPixelDensity_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetPixelDensity();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetPixelDensity_PGM_Positive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetPixelDensity();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetPixelDensity_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetPixelDensity();
        Assert.True(val > 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_PixelDensityPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetPixelDensity();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_PixelDensityPositive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetPixelDensity();
        Assert.True(val > 0.0);
    }
}
