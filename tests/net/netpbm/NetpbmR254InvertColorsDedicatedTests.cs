// Tests for NetpbmImage.InvertColors dedicated coverage.
// Sprint: ff-sprint-s247-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R254

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R254: Dedicated tests for NetpbmImage.InvertColors().
/// InvertColors transforms each pixel value: pixel = MaxValue - pixel, IN PLACE (void return).
/// Dimensions, format, and MaxValue are preserved.
/// Covers: width unchanged; height unchanged; format unchanged; MaxValue unchanged;
/// pixel becomes MaxValue-original; zero pixel becomes MaxValue; MaxValue pixel becomes zero;
/// double invert restores original; dogfood Create->SetPixel->Invert->verify;
/// dogfood all-values-in-range after invert.
/// </summary>
public class NetpbmR254InvertColorsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Dimension/format preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InvertColors_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.InvertColors();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void InvertColors_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.InvertColors();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void InvertColors_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.InvertColors();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void InvertColors_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.InvertColors();
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Pixel transform tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InvertColors_PixelBecomesMaxValueMinusOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        img.InvertColors();
        Assert.Equal(155, img.GetPixel(1, 1)); // 255 - 100 = 155
    }

    [Fact]
    public void InvertColors_ZeroPixel_BecomesMaxValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);
        img.InvertColors();
        Assert.Equal(255, img.GetPixel(0, 0));
    }

    [Fact]
    public void InvertColors_MaxValuePixel_BecomesZero()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 255);
        img.InvertColors();
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    [Fact]
    public void InvertColors_DoubleInvert_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(2, 1, 128);
        img.SetPixel(3, 3, 200);
        int p00 = img.GetPixel(0, 0);
        int p21 = img.GetPixel(2, 1);
        int p33 = img.GetPixel(3, 3);
        img.InvertColors();
        img.InvertColors();
        Assert.Equal(p00, img.GetPixel(0, 0));
        Assert.Equal(p21, img.GetPixel(2, 1));
        Assert.Equal(p33, img.GetPixel(3, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetKnownPixel_VerifyInversion()
    {
        // Set multiple pixels with known values, verify all are inverted correctly
        var img = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 1, 200);
        img.InvertColors();
        Assert.Equal(205, img.GetPixel(0, 0)); // 255 - 50
        Assert.Equal(155, img.GetPixel(1, 0)); // 255 - 100
        Assert.Equal(55, img.GetPixel(2, 1));  // 255 - 200
    }

    [Fact]
    public void DogfoodPipeline_AllPixelsInRangeAfterInvert()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 1, 127);
        img.SetPixel(2, 2, 255);
        img.InvertColors();
        // After invert all pixels must still be in [0, MaxValue]
        Assert.InRange(img.GetPixel(0, 0), 0, img.MaxValue);
        Assert.InRange(img.GetPixel(1, 1), 0, img.MaxValue);
        Assert.InRange(img.GetPixel(2, 2), 0, img.MaxValue);
    }
}
