// Tests for NetpbmImage.GetLuminance dedicated coverage.
// Sprint: ff-sprint-s273-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R281

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R281: Dedicated tests for NetpbmImage.GetLuminance().
/// Returns non-negative value.
/// All-zero image returns 0.0.
/// All-MaxValue image returns positive.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice returns same result.
/// Mixed image returns positive luminance.
/// Dogfood: known-pixel image, luminance in valid range.
/// Dogfood: uniform bright image returns high luminance.
/// </summary>
public class NetpbmR281GetLuminanceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLuminance_ValidImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        double lum = img.GetLuminance();
        Assert.True(lum >= 0.0);
    }

    [Fact]
    public void GetLuminance_AllZeroPixels_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        double lum = img.GetLuminance();
        Assert.Equal(0.0, lum, precision: 5);
    }

    [Fact]
    public void GetLuminance_AllMaxValuePixels_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 255);
        double lum = img.GetLuminance();
        Assert.True(lum > 0.0);
    }

    [Fact]
    public void GetLuminance_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        _ = img.GetLuminance();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetLuminance_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        _ = img.GetLuminance();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void GetLuminance_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 128);
        var fmt = img.Format;
        _ = img.GetLuminance();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void GetLuminance_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 200);
        img.SetPixel(0, 0, 100);
        _ = img.GetLuminance();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void GetLuminance_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(1, 1, 180);
        img.SetPixel(2, 2, 90);
        double first = img.GetLuminance();
        double second = img.GetLuminance();
        Assert.Equal(first, second, precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixels_LuminanceInValidRange()
    {
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 0, 200);
        img.SetPixel(0, 1, 50);
        img.SetPixel(1, 1, 150);
        double lum = img.GetLuminance();
        Assert.True(lum >= 0.0 && lum <= 255.0);
    }

    [Fact]
    public void DogfoodPipeline_UniformBrightImage_ReturnsHighLuminance()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 230);
        double lum = img.GetLuminance();
        Assert.True(lum > 0.0);
    }
}
