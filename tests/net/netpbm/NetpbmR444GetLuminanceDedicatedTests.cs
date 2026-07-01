// Tests for NetpbmImage.GetLuminance dedicated coverage.
// Sprint: ff-sprint-s426-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R444

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R444: Dedicated tests for NetpbmImage.GetLuminance().
/// Returns non-negative value.
/// Width unchanged after GetLuminance.
/// Height unchanged after GetLuminance.
/// Format unchanged after GetLuminance.
/// MaxValue unchanged after GetLuminance.
/// Idempotent (called twice same result).
/// PBM luminance non-negative.
/// PGM luminance non-negative.
/// PPM luminance non-negative.
/// Dogfood: 4x4 PGM luminance non-negative.
/// Dogfood: 4x4 PPM luminance non-negative.
/// </summary>
public class NetpbmR444GetLuminanceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLuminance_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double lum = img.GetLuminance();
        Assert.True(lum >= 0.0);
    }

    [Fact]
    public void GetLuminance_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetLuminance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetLuminance_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetLuminance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetLuminance_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetLuminance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetLuminance_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetLuminance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetLuminance_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetLuminance();
        double second = img.GetLuminance();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetLuminance_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetLuminance() >= 0.0);
    }

    [Fact]
    public void GetLuminance_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetLuminance() >= 0.0);
    }

    [Fact]
    public void GetLuminance_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetLuminance() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_LuminanceNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetLuminance() >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_LuminanceNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetLuminance() >= 0.0);
    }
}
