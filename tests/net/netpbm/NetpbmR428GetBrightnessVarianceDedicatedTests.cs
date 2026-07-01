// Tests for NetpbmImage.GetBrightnessVariance dedicated coverage.
// Sprint: ff-sprint-s410-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R428

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R428: Dedicated tests for NetpbmImage.GetBrightnessVariance().
/// Returns non-negative value.
/// Width unchanged after GetBrightnessVariance.
/// Height unchanged after GetBrightnessVariance.
/// Format unchanged after GetBrightnessVariance.
/// MaxValue unchanged after GetBrightnessVariance.
/// Idempotent (called twice same result).
/// PBM variance non-negative.
/// PGM variance non-negative.
/// PPM variance non-negative.
/// Dogfood: 4x4 PGM variance non-negative.
/// Dogfood: 4x4 PPM variance non-negative.
/// </summary>
public class NetpbmR428GetBrightnessVarianceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightnessVariance_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double variance = img.GetBrightnessVariance();
        Assert.True(variance >= 0);
    }

    [Fact]
    public void GetBrightnessVariance_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetBrightnessVariance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBrightnessVariance_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetBrightnessVariance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBrightnessVariance_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetBrightnessVariance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBrightnessVariance_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetBrightnessVariance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBrightnessVariance_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetBrightnessVariance();
        double second = img.GetBrightnessVariance();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBrightnessVariance_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetBrightnessVariance() >= 0);
    }

    [Fact]
    public void GetBrightnessVariance_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetBrightnessVariance() >= 0);
    }

    [Fact]
    public void GetBrightnessVariance_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetBrightnessVariance() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_VarianceNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetBrightnessVariance() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_VarianceNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetBrightnessVariance() >= 0);
    }
}
