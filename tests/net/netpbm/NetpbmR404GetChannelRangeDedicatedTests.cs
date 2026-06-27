// Tests for NetpbmImage.GetChannelRange dedicated coverage.
// Sprint: ff-sprint-s391-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R404

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R404: Dedicated tests for NetpbmImage.GetChannelRange().
/// Returns non-negative value.
/// Width unchanged after GetChannelRange.
/// Height unchanged after GetChannelRange.
/// Format unchanged after GetChannelRange.
/// MaxValue unchanged after GetChannelRange.
/// Idempotent (called twice same result).
/// PBM range non-negative.
/// PGM range non-negative.
/// PPM range non-negative.
/// Dogfood: 4x4 PGM range non-negative.
/// Dogfood: 4x4 PPM range non-negative.
/// </summary>
public class NetpbmR404GetChannelRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelRange_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int range = img.GetChannelRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetChannelRange_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetChannelRange();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetChannelRange_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetChannelRange();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetChannelRange_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetChannelRange();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetChannelRange_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetChannelRange();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetChannelRange_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetChannelRange();
        int second = img.GetChannelRange();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetChannelRange_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int range = img.GetChannelRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetChannelRange_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int range = img.GetChannelRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetChannelRange_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int range = img.GetChannelRange();
        Assert.True(range >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_RangeNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int range = img.GetChannelRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_RangeNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int range = img.GetChannelRange();
        Assert.True(range >= 0);
    }
}
