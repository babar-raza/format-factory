// Tests for NetpbmImage.GetPixelValueRange dedicated coverage.
// Sprint: ff-sprint-s416-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R434

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R434: Dedicated tests for NetpbmImage.GetPixelValueRange().
/// Returns non-negative range.
/// Range within [0, MaxValue].
/// Width unchanged after GetPixelValueRange.
/// Height unchanged after GetPixelValueRange.
/// Format unchanged after GetPixelValueRange.
/// MaxValue unchanged after GetPixelValueRange.
/// Idempotent (called twice same result).
/// PBM range non-negative.
/// PGM range non-negative.
/// PPM range non-negative.
/// Dogfood: 4x4 PGM range within MaxValue.
/// </summary>
public class NetpbmR434GetPixelValueRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValueRange_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int range = img.GetPixelValueRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetPixelValueRange_WithinMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int range = img.GetPixelValueRange();
        Assert.True(range <= img.MaxValue);
    }

    [Fact]
    public void GetPixelValueRange_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelValueRange_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelValueRange_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelValueRange_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelValueRange_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetPixelValueRange();
        int second = img.GetPixelValueRange();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPixelValueRange_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetPixelValueRange() >= 0);
    }

    [Fact]
    public void GetPixelValueRange_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetPixelValueRange() >= 0);
    }

    [Fact]
    public void GetPixelValueRange_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetPixelValueRange() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_RangeWithinMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int range = img.GetPixelValueRange();
        Assert.True(range >= 0 && range <= img.MaxValue);
    }
}
