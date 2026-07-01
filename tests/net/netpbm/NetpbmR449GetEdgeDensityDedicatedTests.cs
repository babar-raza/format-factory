// Tests for NetpbmImage.GetEdgeDensity dedicated coverage.
// Sprint: ff-sprint-s431-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R449

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R449: Dedicated tests for NetpbmImage.GetEdgeDensity().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM edge density non-negative.
/// </summary>
public class NetpbmR449GetEdgeDensityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeDensity_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetEdgeDensity();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetEdgeDensity_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEdgeDensity_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEdgeDensity_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEdgeDensity_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetEdgeDensity();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEdgeDensity_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetEdgeDensity();
        double second = img.GetEdgeDensity();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetEdgeDensity_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetEdgeDensity();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetEdgeDensity_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetEdgeDensity();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetEdgeDensity_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetEdgeDensity();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_EdgeDensityNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetEdgeDensity();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_EdgeDensityNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetEdgeDensity();
        Assert.True(val >= 0.0);
    }
}
