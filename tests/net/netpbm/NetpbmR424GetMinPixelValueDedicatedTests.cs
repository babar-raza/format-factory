// Tests for NetpbmImage.GetMinPixelValue dedicated coverage.
// Sprint: ff-sprint-s406-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R424

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R424: Dedicated tests for NetpbmImage.GetMinPixelValue().
/// Returns non-negative value.
/// Result less than or equal to MaxValue.
/// Width unchanged after GetMinPixelValue.
/// Height unchanged after GetMinPixelValue.
/// Format unchanged after GetMinPixelValue.
/// MaxValue unchanged after GetMinPixelValue.
/// Idempotent (called twice same result).
/// PBM min non-negative.
/// PGM min non-negative.
/// PPM min non-negative.
/// Dogfood: 4x4 PGM min non-negative.
/// Dogfood: 4x4 PPM min <= MaxValue.
/// </summary>
public class NetpbmR424GetMinPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinPixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int min = img.GetMinPixelValue();
        Assert.True(min >= 0);
    }

    [Fact]
    public void GetMinPixelValue_LessThanOrEqualMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int min = img.GetMinPixelValue();
        Assert.True(min <= img.MaxValue);
    }

    [Fact]
    public void GetMinPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMinPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMinPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMinPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMinPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMinPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetMinPixelValue();
        int second = img.GetMinPixelValue();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMinPixelValue_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetMinPixelValue() >= 0);
    }

    [Fact]
    public void GetMinPixelValue_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetMinPixelValue() >= 0);
    }

    [Fact]
    public void GetMinPixelValue_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetMinPixelValue() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_MinNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetMinPixelValue() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_MinLessThanOrEqualMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetMinPixelValue() <= img.MaxValue);
    }
}
