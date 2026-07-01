// Tests for NetpbmImage.GetSaturation dedicated coverage.
// Sprint: ff-sprint-s424-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R442

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R442: Dedicated tests for NetpbmImage.GetSaturation().
/// Returns non-negative value.
/// Width unchanged after GetSaturation.
/// Height unchanged after GetSaturation.
/// Format unchanged after GetSaturation.
/// MaxValue unchanged after GetSaturation.
/// Idempotent (called twice same result).
/// PBM saturation non-negative.
/// PGM saturation non-negative.
/// PPM saturation non-negative.
/// Dogfood: 4x4 PGM saturation non-negative.
/// Dogfood: 4x4 PPM saturation non-negative.
/// </summary>
public class NetpbmR442GetSaturationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSaturation_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double sat = img.GetSaturation();
        Assert.True(sat >= 0.0);
    }

    [Fact]
    public void GetSaturation_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetSaturation();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSaturation_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetSaturation();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSaturation_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetSaturation();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSaturation_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetSaturation();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSaturation_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetSaturation();
        double second = img.GetSaturation();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSaturation_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetSaturation() >= 0.0);
    }

    [Fact]
    public void GetSaturation_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetSaturation() >= 0.0);
    }

    [Fact]
    public void GetSaturation_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetSaturation() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_SaturationNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetSaturation() >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_SaturationNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetSaturation() >= 0.0);
    }
}
