// Tests for NetpbmImage.GetBlurRadius dedicated coverage.
// Sprint: ff-sprint-s432-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R450

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R450: Dedicated tests for NetpbmImage.GetBlurRadius().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM blur radius non-negative.
/// </summary>
public class NetpbmR450GetBlurRadiusDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlurRadius_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetBlurRadius();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetBlurRadius_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetBlurRadius();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBlurRadius_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetBlurRadius();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBlurRadius_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetBlurRadius();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBlurRadius_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetBlurRadius();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBlurRadius_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetBlurRadius();
        double second = img.GetBlurRadius();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBlurRadius_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetBlurRadius();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetBlurRadius_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetBlurRadius();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetBlurRadius_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetBlurRadius();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_BlurRadiusNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetBlurRadius();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_BlurRadiusNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetBlurRadius();
        Assert.True(val >= 0.0);
    }
}
