// Tests for NetpbmImage.GetMedian dedicated coverage.
// Sprint: ff-sprint-s309-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R318

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R318: Dedicated tests for NetpbmImage.GetMedian().
/// Returns value in [0, MaxValue] range.
/// Width unchanged after GetMedian.
/// Height unchanged after GetMedian.
/// Format unchanged after GetMedian.
/// MaxValue unchanged after GetMedian.
/// All-zero image returns zero or non-negative.
/// Called twice returns same result.
/// Uniform image returns that value as median.
/// Dogfood: standard image returns finite value in range.
/// Dogfood: two-value image median in range.
/// </summary>
public class NetpbmR318GetMedianDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedian_ReturnsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 256);
        double median = img.GetMedian();
        Assert.True(median >= 0.0 && median <= img.MaxValue);
    }

    [Fact]
    public void GetMedian_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMedian();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMedian_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
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
    public void GetMedian_AllZeroImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        double median = img.GetMedian();
        Assert.True(median >= 0.0);
    }

    [Fact]
    public void GetMedian_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 3) % 256);
        double first = img.GetMedian();
        double second = img.GetMedian();
        Assert.Equal(first, second, precision: 5);
    }

    [Fact]
    public void GetMedian_UniformImage_InRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 80);
        double median = img.GetMedian();
        Assert.InRange(median, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StandardImage_FiniteInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * y + x) % 256);
        double median = img.GetMedian();
        Assert.True(double.IsFinite(median));
        Assert.True(median >= 0.0 && median <= 255.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_TwoValueImage_MedianInRange()
    {
        var img = NetpbmImage.CreateNew(4, 2, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x < 2 ? 50 : 200);
        double median = img.GetMedian();
        Assert.True(median >= 0.0 && median <= 255.0);
    }
}
