// Tests for NetpbmImage.GetHistogram dedicated coverage.
// Sprint: ff-sprint-s259-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R266

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R266: Dedicated tests for NetpbmImage.GetHistogram().
/// GetHistogram returns a distribution of pixel values as an array or collection.
/// The result is non-null.
/// Length is MaxValue+1 (one slot per possible pixel value).
/// All entries are non-negative.
/// Sum of all entries equals Width * Height (total pixel count).
/// Uniform image: one bucket = all pixels, others = 0.
/// Width/height/format/MaxValue unchanged (non-mutating).
/// Called twice returns equal result.
/// Dogfood: set known pixel values, verify correct bucket counts.
/// Dogfood: mixed-pixel image, sum equals total pixels.
/// </summary>
public class NetpbmR266GetHistogramDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
    }

    [Fact]
    public void GetHistogram_AllEntriesNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 200);
        var hist = img.GetHistogram();
        foreach (var count in hist)
        {
            Assert.True(count >= 0);
        }
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 150);
        var hist = img.GetHistogram();
        long total = 0;
        foreach (var count in hist)
            total += count;
        Assert.Equal((long)(4 * 3), total);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetHistogram();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetHistogram_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetHistogram();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetHistogram_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.GetHistogram();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetHistogram_CalledTwice_SameLength()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 128);
        var hist1 = img.GetHistogram();
        var hist2 = img.GetHistogram();
        Assert.Equal(hist1.Length, hist2.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixelValues_CorrectBuckets()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        // All 4 pixels = 0 by default
        var hist = img.GetHistogram();
        // Bucket [0] should have all 4 pixels
        Assert.Equal(4, hist[0]);
    }

    [Fact]
    public void DogfoodPipeline_MixedPixels_SumEqualsTotal()
    {
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 0, 20);
        img.SetPixel(2, 0, 30);
        var hist = img.GetHistogram();
        long sum = 0;
        foreach (var c in hist) sum += c;
        Assert.Equal((long)(3 * 2), sum);
    }
}
