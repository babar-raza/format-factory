// Tests for NetpbmImage.GetHistogram dedicated coverage.
// Sprint: ff-sprint-s220-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R227

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R227: Dedicated tests for NetpbmImage.GetHistogram().
/// Empty image: returns non-null.
/// Returns array or collection.
/// Format preserved after call.
/// MaxValue preserved after call.
/// Dimensions preserved after call.
/// Uniform image: single bin has count = width*height.
/// Result length >= 1.
/// All bin counts non-negative.
/// Sum of bins equals total pixel count.
/// Dogfood: two-value image bins both non-zero.
/// </summary>
public class NetpbmR227GetHistogramTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
    }

    [Fact]
    public void GetHistogram_ResultLengthAtLeastOne()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 7);
        var hist = img.GetHistogram();
        Assert.True(hist.Length >= 1);
    }

    [Fact]
    public void GetHistogram_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetHistogram();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetHistogram_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 100);
        img.GetHistogram();
        Assert.Equal(100, img.MaxValue);
    }

    [Fact]
    public void GetHistogram_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(5, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetHistogram();
        Assert.Equal(5, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void GetHistogram_UniformImage_SingleBinHasAllPixels()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        // All pixels are 0 by default
        var hist = img.GetHistogram();
        // Bin 0 should contain all 16 pixels
        Assert.Equal(16, hist[0]);
    }

    [Fact]
    public void GetHistogram_AllBinCountsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 7);
        var hist = img.GetHistogram();
        foreach (var bin in hist)
            Assert.True(bin >= 0);
    }

    [Fact]
    public void GetHistogram_SumEqualsTotalPixelCount()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5, maxValue: 7);
        img.SetPixel(0, 0, 3);
        img.SetPixel(1, 1, 5);
        var hist = img.GetHistogram();
        long sum = 0;
        foreach (var bin in hist) sum += bin;
        Assert.Equal(12, sum);
    }

    [Fact]
    public void GetHistogram_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 7);
        img.SetPixel(0, 0, 3);
        var h1 = img.GetHistogram();
        var h2 = img.GetHistogram();
        Assert.Equal(h1.Length, h2.Length);
        for (int i = 0; i < h1.Length; i++)
            Assert.Equal(h1[i], h2[i]);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoValueImage_BothBinsNonZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 7);
        // Set half pixels to 0, half to 7
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                if ((x + y) % 2 == 0) img.SetPixel(x, y, 7);
        var hist = img.GetHistogram();
        Assert.True(hist[0] > 0);
        Assert.True(hist[7] > 0);
    }
}
