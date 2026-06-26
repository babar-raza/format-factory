// Tests for NetpbmImage.GetStandardDeviation dedicated coverage.
// Sprint: ff-sprint-s260-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R267

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R267: Dedicated tests for NetpbmImage.GetStandardDeviation().
/// GetStandardDeviation returns a measure of pixel value spread as a double.
/// Returns non-negative value.
/// Uniform image (all same pixel value) returns 0.0.
/// Image with varied pixels returns positive value.
/// Width/height/format/MaxValue unchanged (non-mutating).
/// Called twice returns same result.
/// Dogfood: set min and max pixels, verify StdDev > 0.
/// Dogfood: all-zero image, StdDev = 0.
/// </summary>
public class NetpbmR267GetStandardDeviationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStandardDeviation_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 200);
        double stdDev = img.GetStandardDeviation();
        Assert.True(stdDev >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        // Set all pixels to the same value
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                img.SetPixel(c, r, 128);
        double stdDev = img.GetStandardDeviation();
        Assert.Equal(0.0, stdDev, precision: 5);
    }

    [Fact]
    public void GetStandardDeviation_VariedPixels_ReturnsPositive()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(2, 2, 255);
        double stdDev = img.GetStandardDeviation();
        Assert.True(stdDev > 0.0);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStandardDeviation_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetStandardDeviation();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetStandardDeviation_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetStandardDeviation();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetStandardDeviation_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.GetStandardDeviation();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetStandardDeviation_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 150);
        img.GetStandardDeviation();
        Assert.Equal(150, img.MaxValue);
    }

    [Fact]
    public void GetStandardDeviation_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 30);
        img.SetPixel(2, 2, 200);
        double first = img.GetStandardDeviation();
        double second = img.GetStandardDeviation();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MinMaxPixels_StdDevPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);    // min
        img.SetPixel(3, 3, 255);  // max
        double stdDev = img.GetStandardDeviation();
        Assert.True(stdDev > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_AllZeroImage_StdDevIsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        // All pixels default to 0
        double stdDev = img.GetStandardDeviation();
        Assert.Equal(0.0, stdDev, precision: 5);
    }
}
