// Tests for NetpbmImage.GetBrightness dedicated coverage.
// Sprint: ff-sprint-s192-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R193

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R193: Dedicated tests for NetpbmImage.GetBrightness().
/// Returns a double in [0.0, 1.0] representing average pixel brightness.
/// Zero-pixel image (Width=0 or Height=0) or MaxValue=0 returns 0.0.
/// Black PGM image (all zeros) returns 0.0.
/// PGM fully white image returns 1.0.
/// PGM mid-value image returns ~0.5.
/// PPM uses luma formula (0.299R + 0.587G + 0.114B) / MaxValue.
/// PPM black image returns 0.0.
/// PPM white image returns 1.0.
/// Result is always in [0.0, 1.0].
/// Covers: black PGM returns 0; white PGM returns 1; PGM mid returns ~0.5;
/// PPM black returns 0; PPM white returns 1; result in [0,1];
/// PBM all-zero returns 0; PBM all-one returns 1;
/// dogfood PGM uniform mid brightness; dogfood PPM result non-negative.
/// </summary>
public class NetpbmR193GetBrightnessTests
{
    // -------------------------------------------------------------------------
    // PGM tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_PgmBlackImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        // All pixels default to 0
        Assert.Equal(0.0, img.GetBrightness(), precision: 5);
    }

    [Fact]
    public void GetBrightness_PgmWhiteImage_ReturnsOne()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, img.MaxValue);
        Assert.Equal(1.0, img.GetBrightness(), precision: 5);
    }

    [Fact]
    public void GetBrightness_PgmMidValue_ReturnsHalf()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        int mid = img.MaxValue / 2;
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, (byte)mid);
        var brightness = img.GetBrightness();
        Assert.InRange(brightness, 0.4, 0.6);
    }

    // -------------------------------------------------------------------------
    // PPM tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_PpmBlackImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        // All channels default to 0
        Assert.Equal(0.0, img.GetBrightness(), precision: 5);
    }

    [Fact]
    public void GetBrightness_PpmWhiteImage_ReturnsOne()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        byte max = (byte)img.MaxValue;
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixelColor(r, c, max, max, max);
        Assert.Equal(1.0, img.GetBrightness(), precision: 5);
    }

    [Fact]
    public void GetBrightness_ResultInRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, (byte)(r * 20 + c * 10));
        var b = img.GetBrightness();
        Assert.InRange(b, 0.0, 1.0);
    }

    // -------------------------------------------------------------------------
    // PBM tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_PbmAllZero_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P1);
        Assert.Equal(0.0, img.GetBrightness(), precision: 5);
    }

    [Fact]
    public void GetBrightness_PbmAllOne_ReturnsOne()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P1);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, 1);
        Assert.Equal(1.0, img.GetBrightness(), precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmUniformMid_BrightnessInRange()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        byte mid = (byte)(img.MaxValue / 2);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                img.SetPixel(r, c, mid);
        var b = img.GetBrightness();
        Assert.InRange(b, 0.3, 0.7);
    }

    [Fact]
    public void DogfoodPipeline_PpmMixedPixels_ResultNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixelColor(r, c, (byte)(r * 50), (byte)(c * 40), 100);
        var b = img.GetBrightness();
        Assert.True(b >= 0.0);
    }
}
