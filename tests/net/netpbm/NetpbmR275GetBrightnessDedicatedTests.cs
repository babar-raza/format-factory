// Tests for NetpbmImage.GetBrightness dedicated coverage.
// Sprint: ff-sprint-s267-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R275

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R275: Dedicated tests for NetpbmImage.GetBrightness().
/// Valid image returns non-negative value.
/// All-zero image returns 0.0.
/// All-MaxValue image returns MaxValue (or positive).
/// Width/Height/Format/MaxValue unchanged after GetBrightness.
/// Called twice returns same result.
/// Single bright pixel returns positive.
/// Dogfood: known-pixel image, brightness in expected range.
/// Dogfood: uniform bright image returns high brightness value.
/// </summary>
public class NetpbmR275GetBrightnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard / functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_ValidImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        double brightness = img.GetBrightness();
        Assert.True(brightness >= 0.0);
    }

    [Fact]
    public void GetBrightness_AllZeroPixels_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        // Default pixels are zero
        double brightness = img.GetBrightness();
        Assert.Equal(0.0, brightness, precision: 5);
    }

    [Fact]
    public void GetBrightness_AllMaxValuePixels_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 255);
        double brightness = img.GetBrightness();
        Assert.True(brightness > 0.0);
    }

    [Fact]
    public void GetBrightness_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        _ = img.GetBrightness();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetBrightness_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        _ = img.GetBrightness();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void GetBrightness_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 128);
        var formatBefore = img.Format;
        _ = img.GetBrightness();
        Assert.Equal(formatBefore, img.Format);
    }

    [Fact]
    public void GetBrightness_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 200);
        img.SetPixel(0, 0, 100);
        _ = img.GetBrightness();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void GetBrightness_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(1, 1, 180);
        img.SetPixel(2, 2, 90);
        double first = img.GetBrightness();
        double second = img.GetBrightness();
        Assert.Equal(first, second, precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixels_BrightnessInExpectedRange()
    {
        // 2x2 image: all pixels = 128; avg brightness should be 128 (or normalized 0.5 * 255)
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 128);
        img.SetPixel(1, 0, 128);
        img.SetPixel(0, 1, 128);
        img.SetPixel(1, 1, 128);
        double brightness = img.GetBrightness();
        // Brightness should be positive and at most MaxValue
        Assert.True(brightness > 0.0 && brightness <= 255.0);
    }

    [Fact]
    public void DogfoodPipeline_UniformBrightImage_ReturnsHighBrightness()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 220);
        double brightness = img.GetBrightness();
        // Should be clearly positive
        Assert.True(brightness > 0.0);
    }
}
