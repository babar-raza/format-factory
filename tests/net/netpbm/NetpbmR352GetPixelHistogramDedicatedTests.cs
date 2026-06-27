// Tests for NetpbmImage.GetPixelHistogram dedicated coverage.
// Sprint: ff-sprint-s339-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R352

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R352: Dedicated tests for NetpbmImage.GetPixelHistogram().
/// Valid image ok.
/// Returns non-null.
/// Width unchanged after GetPixelHistogram.
/// Height unchanged after GetPixelHistogram.
/// Format unchanged after GetPixelHistogram.
/// MaxValue unchanged after GetPixelHistogram.
/// All-zero image: zero bucket has count equal to pixel count.
/// Idempotent (called twice non-null).
/// Dogfood: uniform image histogram has one non-zero bucket.
/// Dogfood: mixed image histogram has multiple buckets.
/// </summary>
public class NetpbmR352GetPixelHistogramDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelHistogram_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetPixelHistogram());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelHistogram_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var histogram = img.GetPixelHistogram();
        Assert.NotNull(histogram);
    }

    [Fact]
    public void GetPixelHistogram_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetPixelHistogram();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelHistogram_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetPixelHistogram();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelHistogram_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetPixelHistogram();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelHistogram_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetPixelHistogram();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelHistogram_AllZeroImage_ZeroBucketHasPixelCount()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        // All pixels are 0 by default
        var histogram = img.GetPixelHistogram();
        Assert.NotNull(histogram);
        Assert.True(histogram.ContainsKey(0));
        Assert.Equal(16, histogram[0]); // 4x4 = 16 pixels
    }

    [Fact]
    public void GetPixelHistogram_CalledTwice_BothNonNull()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        var first = img.GetPixelHistogram();
        var second = img.GetPixelHistogram();
        Assert.NotNull(first);
        Assert.NotNull(second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_OneNonZeroBucket()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(128);
        var histogram = img.GetPixelHistogram();
        Assert.NotNull(histogram);
        int nonZeroBuckets = 0;
        foreach (var kvp in histogram)
            if (kvp.Value > 0) nonZeroBuckets++;
        Assert.Equal(1, nonZeroBuckets);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_MultipleBuckets()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 150);
        img.SetPixel(2, 0, 200);
        var histogram = img.GetPixelHistogram();
        Assert.NotNull(histogram);
        Assert.True(histogram.Count >= 2);
    }
}
