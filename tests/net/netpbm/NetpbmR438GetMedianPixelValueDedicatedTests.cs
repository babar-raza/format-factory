// Tests for NetpbmImage.GetMedianPixelValue dedicated coverage.
// Sprint: ff-sprint-s420-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R438

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R438: Dedicated tests for NetpbmImage.GetMedianPixelValue().
/// Returns non-negative value.
/// Result within [0, MaxValue].
/// Width unchanged after GetMedianPixelValue.
/// Height unchanged after GetMedianPixelValue.
/// Format unchanged after GetMedianPixelValue.
/// MaxValue unchanged after GetMedianPixelValue.
/// Idempotent (called twice same result).
/// PBM median non-negative.
/// PGM median non-negative.
/// PPM median non-negative.
/// Dogfood: 4x4 PGM median within MaxValue.
/// </summary>
public class NetpbmR438GetMedianPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedianPixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int median = img.GetMedianPixelValue();
        Assert.True(median >= 0);
    }

    [Fact]
    public void GetMedianPixelValue_WithinMaxValueRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int median = img.GetMedianPixelValue();
        Assert.True(median <= img.MaxValue);
    }

    [Fact]
    public void GetMedianPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMedianPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMedianPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMedianPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMedianPixelValue_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetMedianPixelValue();
        int second = img.GetMedianPixelValue();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMedianPixelValue_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetMedianPixelValue() >= 0);
    }

    [Fact]
    public void GetMedianPixelValue_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetMedianPixelValue() >= 0);
    }

    [Fact]
    public void GetMedianPixelValue_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetMedianPixelValue() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_MedianWithinMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int median = img.GetMedianPixelValue();
        Assert.True(median >= 0 && median <= img.MaxValue);
    }
}
