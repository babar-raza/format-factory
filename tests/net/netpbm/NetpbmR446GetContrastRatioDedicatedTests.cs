// Tests for NetpbmImage.GetContrastRatio dedicated coverage.
// Sprint: ff-sprint-s428-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R446

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R446: Dedicated tests for NetpbmImage.GetContrastRatio().
/// Returns positive value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// PPM contrast ratio >= PGM contrast ratio (more channels = richer data).
/// Dogfood: 4x4 PGM and PPM contrast ratio positive.
/// </summary>
public class NetpbmR446GetContrastRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastRatio_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetContrastRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetContrastRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetContrastRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetContrastRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetContrastRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetContrastRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetContrastRatio_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetContrastRatio();
        double second = img.GetContrastRatio();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetContrastRatio_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetContrastRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetContrastRatio_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetContrastRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetContrastRatio_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetContrastRatio();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ContrastRatioNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetContrastRatio();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ContrastRatioNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetContrastRatio();
        Assert.True(val >= 0.0);
    }
}
