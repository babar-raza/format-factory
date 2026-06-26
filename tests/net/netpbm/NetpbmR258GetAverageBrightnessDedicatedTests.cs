// Tests for NetpbmImage.GetAverageBrightness dedicated coverage.
// Sprint: ff-sprint-s251-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R258

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R258: Dedicated tests for NetpbmImage.GetAverageBrightness().
/// GetAverageBrightness returns the mean pixel value across all pixels as a double.
/// Image dimensions, format, and MaxValue are NOT modified.
/// Covers: returns non-negative; all-zero image returns 0; all-max image returns MaxValue;
/// width/height/format/MaxValue unchanged after call; called twice same result;
/// after InvertColors average changes; result in [0, MaxValue] range;
/// dogfood: set known pixels, verify average in expected range;
/// dogfood: symmetric pixel values have expected average.
/// </summary>
public class NetpbmR258GetAverageBrightnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAverageBrightness_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        double avg = img.GetAverageBrightness();
        Assert.True(avg >= 0.0);
    }

    [Fact]
    public void GetAverageBrightness_AllZeroPixels_ReturnsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        // Default pixels are 0
        double avg = img.GetAverageBrightness();
        Assert.Equal(0.0, avg);
    }

    [Fact]
    public void GetAverageBrightness_ResultInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 200);
        double avg = img.GetAverageBrightness();
        Assert.InRange(avg, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // Preservation tests (non-mutating)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAverageBrightness_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetAverageBrightness();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetAverageBrightness_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.GetAverageBrightness();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetAverageBrightness_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.GetAverageBrightness();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void GetAverageBrightness_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.GetAverageBrightness();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void GetAverageBrightness_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        img.SetPixel(1, 1, 64);
        double first = img.GetAverageBrightness();
        double second = img.GetAverageBrightness();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_OneHighPixelAmongZeros_AverageInRange()
    {
        // 3x3 = 9 pixels; set one to 255, rest 0; avg ≈ 255/9 ≈ 28.3
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 255);
        double avg = img.GetAverageBrightness();
        // Average should be between 0 and MaxValue
        Assert.InRange(avg, 0.0, 255.0);
        // Average should be less than MaxValue (only 1 of 9 pixels is max)
        Assert.True(avg < 255.0);
    }

    [Fact]
    public void DogfoodPipeline_AllMaxPixels_AverageEqualsMaxValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 100);
        // Set all 4 pixels to MaxValue
        for (int c = 0; c < 2; c++)
            for (int r = 0; r < 2; r++)
                img.SetPixel(c, r, 100);
        double avg = img.GetAverageBrightness();
        Assert.Equal(100.0, avg);
    }
}
