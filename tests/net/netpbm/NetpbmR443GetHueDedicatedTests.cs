// Tests for NetpbmImage.GetHue dedicated coverage.
// Sprint: ff-sprint-s425-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R443

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R443: Dedicated tests for NetpbmImage.GetHue().
/// Returns non-negative value.
/// Width unchanged after GetHue.
/// Height unchanged after GetHue.
/// Format unchanged after GetHue.
/// MaxValue unchanged after GetHue.
/// Idempotent (called twice same result).
/// PBM hue non-negative.
/// PGM hue non-negative.
/// PPM hue non-negative.
/// Dogfood: 4x4 PGM hue non-negative.
/// Dogfood: 4x4 PPM hue non-negative.
/// </summary>
public class NetpbmR443GetHueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHue_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double hue = img.GetHue();
        Assert.True(hue >= 0.0);
    }

    [Fact]
    public void GetHue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetHue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetHue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetHue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetHue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetHue();
        double second = img.GetHue();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHue_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetHue() >= 0.0);
    }

    [Fact]
    public void GetHue_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetHue() >= 0.0);
    }

    [Fact]
    public void GetHue_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetHue() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_HueNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetHue() >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_HueNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetHue() >= 0.0);
    }
}
