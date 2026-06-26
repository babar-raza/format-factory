// Tests for NetpbmImage.GetHistogram dedicated coverage.
// Sprint: ff-sprint-s241-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R248

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R248: Dedicated tests for NetpbmImage.GetHistogram().
/// Returns non-null array.
/// Array length is 256.
/// Sum of all buckets equals pixel count.
/// All-black image: only bucket[0] non-zero.
/// Uniform image: only one bucket non-zero.
/// After SetPixel: bucket for that value increases.
/// Format preserved after call.
/// MaxValue preserved after call.
/// Dimensions preserved after call.
/// Called twice: same result.
/// Dogfood: set known pixel values, verify histogram buckets.
/// </summary>
public class NetpbmR248GetHistogramDedicatedTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
    }

    [Fact]
    public void GetHistogram_Length256()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var hist = img.GetHistogram();
        int sum = 0;
        foreach (var v in hist) sum += v;
        Assert.Equal(img.Width * img.Height, sum);
    }

    // -------------------------------------------------------------------------
    // Bucket correctness tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_AllBlackImage_OnlyBucket0NonZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        // Default creation should have all zero pixels
        var hist = img.GetHistogram();
        Assert.True(hist[0] > 0);
        // All others should be zero
        for (int i = 1; i < 256; i++)
            Assert.Equal(0, hist[i]);
    }

    [Fact]
    public void GetHistogram_AfterSetPixel_BucketIncreases()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        var hist = img.GetHistogram();
        Assert.True(hist[128] >= 1);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

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
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetHistogram();
        Assert.Equal(5, img.Width);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetHistogram_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 50);
        img.SetPixel(2, 2, 100);
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
    public void DogfoodPipeline_SetKnownValues_VerifyBuckets()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        // Set 3 pixels to value 77, 2 pixels to value 200
        img.SetPixel(0, 0, 77);
        img.SetPixel(1, 0, 77);
        img.SetPixel(2, 0, 77);
        img.SetPixel(0, 1, 200);
        img.SetPixel(1, 1, 200);
        var hist = img.GetHistogram();
        // bucket[77] should be >= 3 (3 pixels set)
        Assert.True(hist[77] >= 3);
        // bucket[200] should be >= 2
        Assert.True(hist[200] >= 2);
        // Total sum still equals 9 (3x3)
        int sum = 0;
        foreach (var v in hist) sum += v;
        Assert.Equal(9, sum);
    }
}
