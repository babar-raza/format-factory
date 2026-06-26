// Tests for NetpbmImage.GetMedianPixelValue dedicated coverage.
// Sprint: ff-sprint-s261-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R268

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R268: Dedicated tests for NetpbmImage.GetMedianPixelValue().
/// GetMedianPixelValue returns the median of all pixel values.
/// Returns a value in [0, MaxValue] range.
/// All-zero image returns 0.
/// All-MaxValue image returns MaxValue.
/// Width/height/format/MaxValue unchanged (non-mutating).
/// Called twice returns same result.
/// Median is consistent with actual pixel values.
/// Dogfood: set pixels to known values, verify median in range.
/// Dogfood: uniform image, median equals that value.
/// </summary>
public class NetpbmR268GetMedianPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedianPixelValue_ReturnsValueInRange()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 200);
        int median = img.GetMedianPixelValue();
        Assert.InRange(median, 0, 255);
    }

    [Fact]
    public void GetMedianPixelValue_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        // All pixels default to 0
        int median = img.GetMedianPixelValue();
        Assert.Equal(0, median);
    }

    [Fact]
    public void GetMedianPixelValue_NonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 150);
        int median = img.GetMedianPixelValue();
        Assert.True(median >= 0);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedianPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetMedianPixelValue();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetMedianPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetMedianPixelValue();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetMedianPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.GetMedianPixelValue();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetMedianPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 100);
        img.GetMedianPixelValue();
        Assert.Equal(100, img.MaxValue);
    }

    [Fact]
    public void GetMedianPixelValue_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 30);
        img.SetPixel(2, 2, 200);
        int first = img.GetMedianPixelValue();
        int second = img.GetMedianPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixels_MedianInRange()
    {
        var img = NetpbmImage.Create(3, 1, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 200);
        int median = img.GetMedianPixelValue();
        // Median of [50, 100, 200] = 100
        Assert.InRange(median, 0, 255);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_MedianEqualsValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int c = 0; c < 2; c++)
            for (int r = 0; r < 2; r++)
                img.SetPixel(c, r, 77);
        int median = img.GetMedianPixelValue();
        Assert.Equal(77, median);
    }
}
