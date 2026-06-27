// Tests for NetpbmImage.GetDynamicRange dedicated coverage.
// Sprint: ff-sprint-s356-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R369

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R369: Dedicated tests for NetpbmImage.GetDynamicRange().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetDynamicRange.
/// Height unchanged after GetDynamicRange.
/// Format unchanged after GetDynamicRange.
/// MaxValue unchanged after GetDynamicRange.
/// Uniform image returns 0.
/// Idempotent (called twice same result).
/// Dogfood: min-max image returns MaxValue range.
/// Dogfood: partial range image returns positive.
/// </summary>
public class NetpbmR369GetDynamicRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDynamicRange_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int range = img.GetDynamicRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetDynamicRange_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        int range = img.GetDynamicRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetDynamicRange_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetDynamicRange_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetDynamicRange_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetDynamicRange_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetDynamicRange();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetDynamicRange_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(100);
        int range = img.GetDynamicRange();
        Assert.Equal(0, range);
    }

    [Fact]
    public void GetDynamicRange_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(75);
        int first = img.GetDynamicRange();
        int second = img.GetDynamicRange();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FullMinMaxRange_Returns255()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(255);
        img.SetPixel(0, 0, 0);
        int range = img.GetDynamicRange();
        Assert.Equal(255, range);
    }

    [Fact]
    public void DogfoodPipeline_PartialRange_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(100);
        img.SetPixel(1, 1, 200);
        int range = img.GetDynamicRange();
        Assert.True(range > 0);
    }
}
