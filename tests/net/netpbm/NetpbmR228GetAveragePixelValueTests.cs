// Tests for NetpbmImage.GetAveragePixelValue dedicated coverage.
// Sprint: ff-sprint-s221-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R228

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R228: Dedicated tests for NetpbmImage.GetAveragePixelValue().
/// Returns non-negative value.
/// Format preserved after call.
/// MaxValue preserved after call.
/// Dimensions preserved after call.
/// Uniform zero image → average = 0.
/// Uniform max image → average = MaxValue.
/// Single pixel image → average = pixel value.
/// Average in range [0, MaxValue].
/// Called twice → same result.
/// Dogfood: set all pixels, verify average within range.
/// </summary>
public class NetpbmR228GetAveragePixelValueTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAveragePixelValue_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var avg = img.GetAveragePixelValue();
        Assert.True(avg >= 0);
    }

    [Fact]
    public void GetAveragePixelValue_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetAveragePixelValue();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetAveragePixelValue_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 100);
        img.GetAveragePixelValue();
        Assert.Equal(100, img.MaxValue);
    }

    [Fact]
    public void GetAveragePixelValue_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(5, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.GetAveragePixelValue();
        Assert.Equal(5, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void GetAveragePixelValue_UniformZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        // All pixels default to 0
        var avg = img.GetAveragePixelValue();
        Assert.Equal(0.0, avg, precision: 1);
    }

    [Fact]
    public void GetAveragePixelValue_UniformMaxImage_ReturnsMaxValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 10);
        for (int y = 0; y < 2; y++)
            for (int x = 0; x < 2; x++)
                img.SetPixel(x, y, 10);
        var avg = img.GetAveragePixelValue();
        Assert.Equal(10.0, avg, precision: 1);
    }

    [Fact]
    public void GetAveragePixelValue_SinglePixel_ReturnsPixelValue()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 42);
        var avg = img.GetAveragePixelValue();
        Assert.Equal(42.0, avg, precision: 1);
    }

    [Fact]
    public void GetAveragePixelValue_InRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        var avg = img.GetAveragePixelValue();
        Assert.InRange(avg, 0.0, 255.0);
    }

    [Fact]
    public void GetAveragePixelValue_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 90);
        var v1 = img.GetAveragePixelValue();
        var v2 = img.GetAveragePixelValue();
        Assert.Equal(v1, v2, precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAllPixels_AverageInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 7);
        int val = 0;
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, val++ % 8);
        var avg = img.GetAveragePixelValue();
        Assert.InRange(avg, 0.0, 7.0);
    }
}
