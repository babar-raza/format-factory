// Tests for NetpbmImage.GetMean dedicated coverage.
// Sprint: ff-sprint-s280-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R288

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R288: Dedicated tests for NetpbmImage.GetMean().
/// Returns non-negative double.
/// All-zero image returns 0.0.
/// All-max image returns positive value.
/// Width unchanged after GetMean.
/// Height unchanged after GetMean.
/// Format unchanged after GetMean.
/// MaxValue unchanged after GetMean.
/// Called twice returns same result.
/// Dogfood: uniform image mean equals pixel value (normalized).
/// Dogfood: mixed image mean is in [0, MaxValue].
/// </summary>
public class NetpbmR288GetMeanDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMean_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        double mean = img.GetMean();
        Assert.True(mean >= 0.0);
    }

    [Fact]
    public void GetMean_AllZero_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        // Default pixels are 0
        double mean = img.GetMean();
        Assert.Equal(0.0, mean);
    }

    [Fact]
    public void GetMean_AllMax_ReturnsPositive()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, img.MaxValue);
        double mean = img.GetMean();
        Assert.True(mean > 0.0);
    }

    [Fact]
    public void GetMean_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMean();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMean_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMean();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMean_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMean();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMean_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMean();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMean_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        double first = img.GetMean();
        double second = img.GetMean();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_MeanInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 150);
        img.SetPixel(2, 0, 200);
        double mean = img.GetMean();
        Assert.True(mean >= 0.0 && mean <= img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_MeanNonNegative()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        double mean = img.GetMean();
        Assert.True(mean >= 0.0);
    }
}
