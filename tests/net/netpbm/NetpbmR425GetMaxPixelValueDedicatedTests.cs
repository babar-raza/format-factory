// Tests for NetpbmImage.GetMaxPixelValue dedicated coverage.
// Sprint: ff-sprint-s407-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R425

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R425: Dedicated tests for NetpbmImage.GetMaxPixelValue().
/// Returns non-negative value.
/// Result less than or equal to MaxValue.
/// Width unchanged after GetMaxPixelValue.
/// Height unchanged after GetMaxPixelValue.
/// Format unchanged after GetMaxPixelValue.
/// MaxValue unchanged after GetMaxPixelValue.
/// Idempotent (called twice same result).
/// PBM max non-negative.
/// PGM max non-negative.
/// PPM max non-negative.
/// Dogfood: 4x4 PGM max <= MaxValue.
/// Dogfood: 4x4 PPM max <= MaxValue.
/// </summary>
public class NetpbmR425GetMaxPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxPixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int max = img.GetMaxPixelValue();
        Assert.True(max >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_LessThanOrEqualMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int max = img.GetMaxPixelValue();
        Assert.True(max <= img.MaxValue);
    }

    [Fact]
    public void GetMaxPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMaxPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMaxPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMaxPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMaxPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMaxPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetMaxPixelValue();
        int second = img.GetMaxPixelValue();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMaxPixelValue_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetMaxPixelValue() >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetMaxPixelValue() >= 0);
    }

    [Fact]
    public void GetMaxPixelValue_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetMaxPixelValue() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_MaxLessThanOrEqualMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetMaxPixelValue() <= img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_MaxLessThanOrEqualMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetMaxPixelValue() <= img.MaxValue);
    }
}
