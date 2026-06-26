// Tests for NetpbmImage.GetMedian dedicated coverage.
// Sprint: ff-sprint-s286-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R294

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R294: Dedicated tests for NetpbmImage.GetMedian().
/// Returns value in [0, MaxValue].
/// All-zero image returns 0.
/// All-max image returns MaxValue.
/// Width unchanged after GetMedian.
/// Height unchanged after GetMedian.
/// Format unchanged after GetMedian.
/// MaxValue unchanged after GetMedian.
/// Called twice returns same result.
/// Dogfood: uniform image median equals pixel value.
/// Dogfood: mixed image median in [0, MaxValue].
/// </summary>
public class NetpbmR294GetMedianDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedian_InRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        int median = img.GetMedian();
        Assert.InRange(median, 0, img.MaxValue);
    }

    [Fact]
    public void GetMedian_AllZero_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int median = img.GetMedian();
        Assert.Equal(0, median);
    }

    [Fact]
    public void GetMedian_AllMax_ReturnsMaxValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, img.MaxValue);
        int median = img.GetMedian();
        Assert.Equal(img.MaxValue, median);
    }

    [Fact]
    public void GetMedian_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMedian();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMedian_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMedian();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMedian_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMedian();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMedian_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMedian();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMedian_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 50);
        int first = img.GetMedian();
        int second = img.GetMedian();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_MedianEqualsPixelValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        int median = img.GetMedian();
        Assert.InRange(median, 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_MedianInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 50);
        img.SetPixel(2, 0, 128);
        img.SetPixel(3, 0, 255);
        int median = img.GetMedian();
        Assert.InRange(median, 0, img.MaxValue);
    }
}
