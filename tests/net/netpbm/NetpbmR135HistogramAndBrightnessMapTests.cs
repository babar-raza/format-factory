// Tests for NetpbmImage.GetHistogram() and NetpbmImage.GetBrightnessMap().
// Sprint: FORMAT-FACTORY-NETPBM-HISTOGRAM-R135-20260626
// Ledger: R135-GOVERNED-DOTNET-NETPBM-HISTOGRAM-BRIGHTNESSMAP-001

using System.Linq;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R135: NetpbmImage.GetHistogram() returns an int[256] histogram where
/// histogram[v] = count of pixels with value v. Sum of all buckets equals PixelCount.
/// NetpbmImage.GetBrightnessMap() returns a double[] with one entry per pixel,
/// normalized to [0.0, 1.0]. Length equals PixelCount.
/// </summary>
public class NetpbmR135HistogramAndBrightnessMapTests
{
    private static NetpbmImage WhitePgm(int width, int height)
    {
        var img = NetpbmImage.Create(width, height, NetpbmFormat.PGM_P2, fill: 255);
        return img;
    }

    private static NetpbmImage BlackPgm(int width, int height)
    {
        return NetpbmImage.Create(width, height, NetpbmFormat.PGM_P2, fill: 0);
    }

    private static NetpbmImage GrayPgm(int width, int height, byte value)
    {
        return NetpbmImage.Create(width, height, NetpbmFormat.PGM_P2, fill: value);
    }

    // ---- GetHistogram: length ----

    [Fact]
    public void GetHistogram_Always_Returns256Buckets()
    {
        var img = WhitePgm(4, 4);
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    // ---- GetHistogram: all-white ----

    [Fact]
    public void GetHistogram_AllWhite_Bucket255EqualPixelCount()
    {
        var img = WhitePgm(3, 3);
        var hist = img.GetHistogram();
        Assert.Equal(img.Width * img.Height, hist[255]);
    }

    [Fact]
    public void GetHistogram_AllWhite_AllOtherBucketsZero()
    {
        var img = WhitePgm(2, 2);
        var hist = img.GetHistogram();
        for (int v = 0; v < 255; v++)
            Assert.Equal(0, hist[v]);
    }

    // ---- GetHistogram: all-black ----

    [Fact]
    public void GetHistogram_AllBlack_Bucket0EqualPixelCount()
    {
        var img = BlackPgm(3, 3);
        var hist = img.GetHistogram();
        Assert.Equal(img.Width * img.Height, hist[0]);
    }

    // ---- GetHistogram: sum equals PixelCount ----

    [Fact]
    public void GetHistogram_Sum_EqualsTotalPixelCount()
    {
        var img = GrayPgm(4, 3, 128);
        var hist = img.GetHistogram();
        long sum = hist.Sum(x => (long)x);
        Assert.Equal(img.Width * img.Height, (int)sum);
    }

    [Fact]
    public void GetHistogram_MixedImage_SumEqualsTotalPixels()
    {
        var img = NetpbmImage.Create(4, 1, NetpbmFormat.PGM_P2, fill: 0);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 100);
        img.SetPixel(0, 2, 150);
        img.SetPixel(0, 3, 200);
        var hist = img.GetHistogram();
        long sum = hist.Sum(x => (long)x);
        Assert.Equal(4, (int)sum);
    }

    // ---- GetBrightnessMap: length ----

    [Fact]
    public void GetBrightnessMap_Always_LengthEqualsPixelCount()
    {
        var img = WhitePgm(3, 4);
        var map = img.GetBrightnessMap();
        Assert.Equal(img.Width * img.Height, map.Length);
    }

    // ---- GetBrightnessMap: all-white ----

    [Fact]
    public void GetBrightnessMap_AllWhite_AllElementsNearOne()
    {
        var img = WhitePgm(2, 2);
        var map = img.GetBrightnessMap();
        foreach (var b in map)
            Assert.InRange(b, 0.99, 1.01);
    }

    // ---- GetBrightnessMap: all-black ----

    [Fact]
    public void GetBrightnessMap_AllBlack_AllElementsNearZero()
    {
        var img = BlackPgm(2, 2);
        var map = img.GetBrightnessMap();
        foreach (var b in map)
            Assert.InRange(b, -0.01, 0.01);
    }

    // ---- Dogfood: histogram + brightness map consistency ----

    [Fact]
    public void DogfoodPipeline_BrightnessMapMean_ApproximatesGetBrightness()
    {
        // Uniform gray image: both metrics should agree
        var img = GrayPgm(5, 5, 128);

        var map         = img.GetBrightnessMap();
        var mapMean     = map.Average();
        var directBrightness = img.GetBrightness();

        Assert.InRange(mapMean, directBrightness - 0.01, directBrightness + 0.01);
    }

    [Fact]
    public void DogfoodPipeline_HistogramAndBrightnessMap_CrossConsistent()
    {
        // 4-pixel image with known values
        var img = NetpbmImage.Create(4, 1, NetpbmFormat.PGM_P2, fill: 0);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 128);
        img.SetPixel(0, 2, 128);
        img.SetPixel(0, 3, 255);

        var hist = img.GetHistogram();
        var map  = img.GetBrightnessMap();

        // Histogram checks
        Assert.Equal(1, hist[0]);
        Assert.Equal(2, hist[128]);
        Assert.Equal(1, hist[255]);
        Assert.Equal(4, hist.Sum());

        // Brightness map length
        Assert.Equal(4, map.Length);

        // Map and stats consistency
        var stats = img.GetStats();
        var mapMean = map.Average();
        Assert.InRange(mapMean * 255.0, stats.Mean - 1.0, stats.Mean + 1.0);
    }
}
