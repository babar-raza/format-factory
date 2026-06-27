// Tests for NetpbmImage.GetMedian dedicated coverage.
// Sprint: ff-sprint-s328-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R340

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R340: Dedicated tests for NetpbmImage.GetMedian().
/// Valid call no exception.
/// Width unchanged after GetMedian.
/// Height unchanged after GetMedian.
/// Format unchanged after GetMedian.
/// MaxValue unchanged after GetMedian.
/// Returns value in [0, MaxValue].
/// All-zero image returns zero median.
/// Idempotent (called twice same result).
/// Uniform image median equals pixel value.
/// Dogfood: alternating image median is non-negative.
/// </summary>
public class NetpbmR340GetMedianDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedian_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 9 + y * 13) % 256);
        var ex = Record.Exception(() => img.GetMedian());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMedian_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMedian();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMedian_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMedian();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMedian_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMedian();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMedian_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMedian();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMedian_ReturnsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 3) % 256);
        double median = img.GetMedian();
        Assert.InRange(median, 0.0, img.MaxValue);
    }

    [Fact]
    public void GetMedian_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double median = img.GetMedian();
        Assert.Equal(0.0, median, precision: 10);
    }

    [Fact]
    public void GetMedian_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 13 + y * 5) % 256);
        double first = img.GetMedian();
        double second = img.GetMedian();
        Assert.Equal(first, second, precision: 10);
    }

    [Fact]
    public void GetMedian_UniformImage_MedianEqualsPixelValue()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 120);
        double median = img.GetMedian();
        Assert.Equal(120.0, median, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AlternatingImage_MedianNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 50 : 200);
        double median = img.GetMedian();
        Assert.True(median >= 0.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
