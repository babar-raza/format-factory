// Tests for NetpbmImage.GetDynamicRange dedicated coverage.
// Sprint: ff-sprint-s433-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R451

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R451: Dedicated tests for NetpbmImage.GetDynamicRange().
/// Returns non-negative value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM dynamic range non-negative.
/// </summary>
public class NetpbmR451GetDynamicRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDynamicRange_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetDynamicRange();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetDynamicRange_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetDynamicRange_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetDynamicRange_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetDynamicRange_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetDynamicRange_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetDynamicRange();
        double second = img.GetDynamicRange();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDynamicRange_PBM_NonNegative()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetDynamicRange();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetDynamicRange_PGM_NonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetDynamicRange();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void GetDynamicRange_PPM_NonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetDynamicRange();
        Assert.True(val >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_DynamicRangeNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetDynamicRange();
        Assert.True(val >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_DynamicRangeNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetDynamicRange();
        Assert.True(val >= 0.0);
    }
}
