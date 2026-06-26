// Tests for NetpbmImage.GetPixelColor, SetPixelColor, ToGrayscale, ToColor, GetStats.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R174

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R174: Tests for NetpbmImage.GetPixelColor, SetPixelColor, ToGrayscale, ToColor, GetStats.
/// GetPixelColor(row,col): returns (R,G,B) tuple for a color image.
/// SetPixelColor(row,col,r,g,b): sets the RGB channels at a pixel.
/// ToGrayscale(): converts color image to grayscale.
/// ToColor(): converts grayscale image to color (3-channel).
/// GetStats(): returns (Mean,Min,Max) triple.
/// Covers: GetPixelColor returns set values; SetPixelColor then GetPixelColor round-trips;
/// GetPixelColor red channel correct; GetPixelColor green channel correct;
/// GetPixelColor blue channel correct; SetPixelColor updates all channels;
/// ToGrayscale width equals original; ToGrayscale height equals original;
/// ToGrayscale format is PGM; ToColor format is PPM;
/// ToColor width unchanged; GetStats mean in valid range;
/// GetStats min le max; dogfood Create->SetPixelColor->GetPixelColor->ToGrayscale->GetStats.
/// </summary>
public class NetpbmR174GetPixelColorAndSetPixelColorTests
{
    private static NetpbmImage CreateColorImage(int width = 4, int height = 4)
    {
        var img = NetpbmImage.Create(width, height, NetpbmFormat.Ppm, 0);
        // Paint a distinct pattern
        for (int r = 0; r < height; r++)
        for (int c = 0; c < width; c++)
            img.SetPixelColor(r, c, (byte)(r * 40), (byte)(c * 40), 128);
        return img;
    }

    // -------------------------------------------------------------------------
    // GetPixelColor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelColor_ReturnsSetValues()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.Ppm, 0);
        img.SetPixelColor(1, 1, 100, 150, 200);
        var (r, g, b) = img.GetPixelColor(1, 1);
        Assert.Equal(100, r);
        Assert.Equal(150, g);
        Assert.Equal(200, b);
    }

    [Fact]
    public void GetPixelColor_RedChannel_Correct()
    {
        var img = CreateColorImage();
        var (r, _, _) = img.GetPixelColor(2, 0);
        Assert.Equal(80, r); // row=2, r=2*40=80
    }

    [Fact]
    public void GetPixelColor_GreenChannel_Correct()
    {
        var img = CreateColorImage();
        var (_, g, _) = img.GetPixelColor(0, 3);
        Assert.Equal(120, g); // col=3, g=3*40=120
    }

    [Fact]
    public void GetPixelColor_BlueChannel_Correct()
    {
        var img = CreateColorImage();
        var (_, _, b) = img.GetPixelColor(1, 2);
        Assert.Equal(128, b); // all pixels have blue=128
    }

    // -------------------------------------------------------------------------
    // SetPixelColor
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixelColor_UpdatesAllChannels()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.Ppm, 0);
        img.SetPixelColor(2, 3, 11, 22, 33);
        var (r, g, b) = img.GetPixelColor(2, 3);
        Assert.Equal(11, r);
        Assert.Equal(22, g);
        Assert.Equal(33, b);
    }

    [Fact]
    public void SetPixelColor_ThenGetPixelColor_RoundTrips()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.Ppm, 255);
        img.SetPixelColor(0, 0, 10, 20, 30);
        img.SetPixelColor(1, 1, 40, 50, 60);
        var (r0, g0, b0) = img.GetPixelColor(0, 0);
        var (r1, g1, b1) = img.GetPixelColor(1, 1);
        Assert.Equal((10, 20, 30), (r0, g0, b0));
        Assert.Equal((40, 50, 60), (r1, g1, b1));
    }

    // -------------------------------------------------------------------------
    // ToGrayscale
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_WidthEqualsOriginal()
    {
        var img = CreateColorImage(6, 4);
        var gray = img.ToGrayscale();
        Assert.Equal(6, gray.Width);
    }

    [Fact]
    public void ToGrayscale_HeightEqualsOriginal()
    {
        var img = CreateColorImage(6, 4);
        var gray = img.ToGrayscale();
        Assert.Equal(4, gray.Height);
    }

    [Fact]
    public void ToGrayscale_FormatIsPgm()
    {
        var img = CreateColorImage();
        var gray = img.ToGrayscale();
        Assert.Equal(NetpbmFormat.Pgm, gray.Format);
    }

    // -------------------------------------------------------------------------
    // ToColor
    // -------------------------------------------------------------------------

    [Fact]
    public void ToColor_FormatIsPpm()
    {
        var gray = NetpbmImage.Create(3, 3, NetpbmFormat.Pgm, 128);
        var color = gray.ToColor();
        Assert.Equal(NetpbmFormat.Ppm, color.Format);
    }

    [Fact]
    public void ToColor_WidthUnchanged()
    {
        var gray = NetpbmImage.Create(5, 3, NetpbmFormat.Pgm, 100);
        var color = gray.ToColor();
        Assert.Equal(5, color.Width);
    }

    // -------------------------------------------------------------------------
    // GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_MeanInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 128);
        var (mean, _, _) = img.GetStats();
        Assert.InRange(mean, 0.0, 255.0);
    }

    [Fact]
    public void GetStats_MinLessThanOrEqualToMax()
    {
        var img = CreateColorImage();
        var (_, min, max) = img.GetStats();
        Assert.True(min <= max);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->SetPixelColor->GetPixelColor->ToGrayscale->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetGetToGrayscaleGetStats_Pipeline()
    {
        // Create a small color image
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Ppm, 0);
        Assert.Equal(NetpbmFormat.Ppm, img.Format);

        // Paint distinct pixels
        img.SetPixelColor(0, 0, 255, 0, 0);   // red
        img.SetPixelColor(0, 1, 0, 255, 0);   // green
        img.SetPixelColor(1, 0, 0, 0, 255);   // blue
        img.SetPixelColor(1, 1, 128, 128, 128); // gray

        // GetPixelColor verifications
        var (r, g, b) = img.GetPixelColor(0, 0);
        Assert.Equal(255, r);
        Assert.Equal(0, g);
        Assert.Equal(0, b);

        // ToGrayscale
        var gray = img.ToGrayscale();
        Assert.Equal(NetpbmFormat.Pgm, gray.Format);
        Assert.Equal(img.Width, gray.Width);
        Assert.Equal(img.Height, gray.Height);

        // GetStats on grayscale
        var (mean, min, max) = gray.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.True(min <= max);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
