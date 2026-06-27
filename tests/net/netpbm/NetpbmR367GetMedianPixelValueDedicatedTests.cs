// Tests for NetpbmImage.GetMedianPixelValue dedicated coverage.
// Sprint: ff-sprint-s354-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R367

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R367: Dedicated tests for NetpbmImage.GetMedianPixelValue().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetMedianPixelValue.
/// Height unchanged after GetMedianPixelValue.
/// Format unchanged after GetMedianPixelValue.
/// MaxValue unchanged after GetMedianPixelValue.
/// Uniform image returns fill value.
/// Idempotent (called twice same result).
/// Dogfood: all-100 image median is 100.
/// Dogfood: mixed image median in [min,max].
/// </summary>
public class NetpbmR367GetMedianPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedianPixelValue_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int median = img.GetMedianPixelValue();
        Assert.True(median >= 0);
    }

    [Fact]
    public void GetMedianPixelValue_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        int median = img.GetMedianPixelValue();
        Assert.True(median >= 0);
    }

    [Fact]
    public void GetMedianPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMedianPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMedianPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMedianPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetMedianPixelValue();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMedianPixelValue_UniformImage_ReturnsFillValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(120);
        int median = img.GetMedianPixelValue();
        Assert.Equal(120, median);
    }

    [Fact]
    public void GetMedianPixelValue_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(90);
        int first = img.GetMedianPixelValue();
        int second = img.GetMedianPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_All100_MedianIs100()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(100);
        int median = img.GetMedianPixelValue();
        Assert.Equal(100, median);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_MedianInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(50);
        img.SetPixel(0, 0, 200);
        img.SetPixel(0, 1, 10);
        int median = img.GetMedianPixelValue();
        Assert.InRange(median, 0, 255);
    }
}
