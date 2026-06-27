// Tests for NetpbmImage.GetPixelValueRange dedicated coverage.
// Sprint: ff-sprint-s350-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R363

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R363: Dedicated tests for NetpbmImage.GetPixelValueRange().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetPixelValueRange.
/// Height unchanged after GetPixelValueRange.
/// Format unchanged after GetPixelValueRange.
/// MaxValue unchanged after GetPixelValueRange.
/// Uniform image returns 0.
/// Idempotent (called twice same result).
/// Dogfood: min=0 max=255 image returns 255.
/// Dogfood: mixed image range > 0.
/// </summary>
public class NetpbmR363GetPixelValueRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValueRange_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int range = img.GetPixelValueRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetPixelValueRange_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        int range = img.GetPixelValueRange();
        Assert.True(range >= 0);
    }

    [Fact]
    public void GetPixelValueRange_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelValueRange_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelValueRange_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelValueRange_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetPixelValueRange();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelValueRange_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(128);
        int range = img.GetPixelValueRange();
        Assert.Equal(0, range);
    }

    [Fact]
    public void GetPixelValueRange_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(64);
        int first = img.GetPixelValueRange();
        int second = img.GetPixelValueRange();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FullRange_Returns255()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(255);
        img.SetPixel(0, 0, 0);
        int range = img.GetPixelValueRange();
        Assert.Equal(255, range);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_RangeGreaterThanZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(50);
        img.SetPixel(2, 2, 200);
        int range = img.GetPixelValueRange();
        Assert.True(range > 0);
    }
}
