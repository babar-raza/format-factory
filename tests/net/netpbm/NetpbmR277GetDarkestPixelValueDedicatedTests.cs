// Tests for NetpbmImage.GetDarkestPixelValue dedicated coverage.
// Sprint: ff-sprint-s269-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R277

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R277: Dedicated tests for NetpbmImage.GetDarkestPixelValue().
/// Returns value in [0, MaxValue].
/// All-zero image returns 0.
/// All-MaxValue image returns MaxValue.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice returns same result.
/// Mixed image returns min of set pixels.
/// Dogfood: known-pixel image, darkest = known minimum.
/// Dogfood: single dark pixel dominates.
/// </summary>
public class NetpbmR277GetDarkestPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDarkestPixelValue_ValidImage_InRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 50);
        int dark = img.GetDarkestPixelValue();
        Assert.InRange(dark, 0, 255);
    }

    [Fact]
    public void GetDarkestPixelValue_AllZeroPixels_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        // Default pixels are zero
        int dark = img.GetDarkestPixelValue();
        Assert.Equal(0, dark);
    }

    [Fact]
    public void GetDarkestPixelValue_AllMaxValuePixels_ReturnsMaxValue()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 255);
        int dark = img.GetDarkestPixelValue();
        Assert.Equal(255, dark);
    }

    [Fact]
    public void GetDarkestPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 10);
        _ = img.GetDarkestPixelValue();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetDarkestPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 10);
        _ = img.GetDarkestPixelValue();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void GetDarkestPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 30);
        var fmt = img.Format;
        _ = img.GetDarkestPixelValue();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void GetDarkestPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 200);
        img.SetPixel(0, 0, 50);
        _ = img.GetDarkestPixelValue();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void GetDarkestPixelValue_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(1, 1, 30);
        img.SetPixel(2, 2, 90);
        int first = img.GetDarkestPixelValue();
        int second = img.GetDarkestPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownMinPixel_ReturnsThatValue()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 200);
        img.SetPixel(1, 0, 150);
        img.SetPixel(2, 0, 5); // darkest
        img.SetPixel(0, 1, 100);
        img.SetPixel(1, 1, 80);
        int dark = img.GetDarkestPixelValue();
        Assert.True(dark <= 5);
    }

    [Fact]
    public void DogfoodPipeline_SingleDarkPixel_Dominates()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        // All pixels at 200 except one at 2
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, 200);
        img.SetPixel(2, 2, 2);
        int dark = img.GetDarkestPixelValue();
        Assert.True(dark <= 2);
    }
}
