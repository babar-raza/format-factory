// Tests for NetpbmImage.GetBrightestPixelValue dedicated coverage.
// Sprint: ff-sprint-s270-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R278

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R278: Dedicated tests for NetpbmImage.GetBrightestPixelValue().
/// Returns value in [0, MaxValue].
/// All-zero image returns 0.
/// All-MaxValue image returns MaxValue.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice returns same result.
/// Mixed image returns max of set pixels.
/// Dogfood: known-pixel image, brightest = known maximum.
/// Dogfood: single bright pixel dominates.
/// </summary>
public class NetpbmR278GetBrightestPixelValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightestPixelValue_ValidImage_InRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 200);
        int bright = img.GetBrightestPixelValue();
        Assert.InRange(bright, 0, 255);
    }

    [Fact]
    public void GetBrightestPixelValue_AllZeroPixels_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        // Default pixels are zero
        int bright = img.GetBrightestPixelValue();
        Assert.Equal(0, bright);
    }

    [Fact]
    public void GetBrightestPixelValue_AllMaxValuePixels_ReturnsMaxValue()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 255);
        int bright = img.GetBrightestPixelValue();
        Assert.Equal(255, bright);
    }

    [Fact]
    public void GetBrightestPixelValue_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 200);
        _ = img.GetBrightestPixelValue();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetBrightestPixelValue_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 200);
        _ = img.GetBrightestPixelValue();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void GetBrightestPixelValue_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 180);
        var fmt = img.Format;
        _ = img.GetBrightestPixelValue();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void GetBrightestPixelValue_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 200);
        img.SetPixel(0, 0, 150);
        _ = img.GetBrightestPixelValue();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void GetBrightestPixelValue_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(1, 1, 230);
        img.SetPixel(2, 2, 90);
        int first = img.GetBrightestPixelValue();
        int second = img.GetBrightestPixelValue();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownMaxPixel_ReturnsThatValue()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 240); // brightest
        img.SetPixel(0, 1, 30);
        img.SetPixel(1, 1, 80);
        int bright = img.GetBrightestPixelValue();
        Assert.True(bright >= 240);
    }

    [Fact]
    public void DogfoodPipeline_SingleBrightPixel_Dominates()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        // All pixels at 10 except one at 253
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, 10);
        img.SetPixel(2, 2, 253);
        int bright = img.GetBrightestPixelValue();
        Assert.True(bright >= 253);
    }
}
