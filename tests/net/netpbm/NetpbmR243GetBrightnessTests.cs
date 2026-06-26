// Tests for NetpbmImage.GetBrightness dedicated coverage.
// Sprint: ff-sprint-s236-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R243

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R243: Dedicated tests for NetpbmImage.GetBrightness().
/// All-black image → brightness near zero.
/// All-white image → brightness near MaxValue.
/// Valid range: brightness in [0.0, MaxValue].
/// Single bright pixel increases brightness.
/// Format PGM_P5 valid result.
/// Format PPM_P6 valid result.
/// Uniform-mid-value → brightness near mid.
/// Consistent: called twice same result.
/// Larger image same uniform brightness as smaller.
/// Dogfood: set pixel, verify brightness changes.
/// </summary>
public class NetpbmR243GetBrightnessTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_AllBlack_NearZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        // All pixels default to 0
        double brightness = img.GetBrightness();
        Assert.True(brightness < 5.0);
    }

    [Fact]
    public void GetBrightness_AllWhite_NearMaxValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int x = 0; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, 255);
        double brightness = img.GetBrightness();
        Assert.True(brightness > 250.0);
    }

    [Fact]
    public void GetBrightness_ValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        double brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.0, 255.0);
    }

    [Fact]
    public void GetBrightness_SingleBrightPixel_IncreasesFromZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        double baseBrightness = img.GetBrightness();
        img.SetPixel(2, 2, 255);
        double newBrightness = img.GetBrightness();
        Assert.True(newBrightness > baseBrightness);
    }

    [Fact]
    public void GetBrightness_PgmP5_ValidResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        var ex = Record.Exception(() => img.GetBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightness_PpmP6_ValidResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        img.SetPixel(1, 1, 100);
        var ex = Record.Exception(() => img.GetBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightness_UniformMidValue_NearMid()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int x = 0; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, 128);
        double brightness = img.GetBrightness();
        Assert.InRange(brightness, 100.0, 155.0);
    }

    [Fact]
    public void GetBrightness_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 180);
        double b1 = img.GetBrightness();
        double b2 = img.GetBrightness();
        Assert.Equal(b1, b2);
    }

    [Fact]
    public void GetBrightness_UniformValue_SameRegardlessOfSize()
    {
        var small = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        var large = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int x = 0; x < 2; x++) for (int y = 0; y < 2; y++) small.SetPixel(x, y, 100);
        for (int x = 0; x < 8; x++) for (int y = 0; y < 8; y++) large.SetPixel(x, y, 100);
        Assert.Equal(small.GetBrightness(), large.GetBrightness());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixel_BrightnessChanges()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        double before = img.GetBrightness();
        for (int x = 0; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, 200);
        double after = img.GetBrightness();
        Assert.True(after > before);
    }
}
