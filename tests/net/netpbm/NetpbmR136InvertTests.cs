// Tests for NetpbmImage.Invert() — in-place pixel value inversion.
// Sprint: FORMAT-FACTORY-NETPBM-INVERT-R136-20260626
// Ledger: R136-GOVERNED-DOTNET-NETPBM-INVERT-001

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R136: NetpbmImage.Invert() inverts each pixel value in-place: value v becomes MaxValue - v.
/// All-white (255) becomes all-black (0) and vice-versa. Double inversion restores the original.
/// Dimensions and format are preserved. Invert works on PGM and PPM images.
/// </summary>
public class NetpbmR136InvertTests
{
    // ---- All-white → all-black ----

    [Fact]
    public void Invert_AllWhitePgm_BecomesAllBlack()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2, fill: 255);
        img.Invert();
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.Equal(0, img.GetPixel(r, c));
    }

    // ---- All-black → all-white ----

    [Fact]
    public void Invert_AllBlackPgm_BecomesAllWhite()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2, fill: 0);
        img.Invert();
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.Equal(255, img.GetPixel(r, c));
    }

    // ---- Single pixel value ----

    [Fact]
    public void Invert_PixelValue128_Becomes127()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P2, fill: 128);
        img.Invert();
        Assert.Equal(127, img.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_PixelValue100_Becomes155()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P2, fill: 100);
        img.Invert();
        Assert.Equal(155, img.GetPixel(0, 0));
    }

    // ---- Double invert restores original ----

    [Fact]
    public void Invert_Twice_RestoresOriginalAllWhite()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, fill: 255);
        img.Invert();
        img.Invert();
        for (int r = 0; r < 2; r++)
            for (int c = 0; c < 2; c++)
                Assert.Equal(255, img.GetPixel(r, c));
    }

    [Fact]
    public void Invert_Twice_RestoresOriginalMixedValues()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, fill: 0);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 100);
        img.SetPixel(1, 0, 150);
        img.SetPixel(1, 1, 200);

        // Snapshot originals
        byte p00 = img.GetPixel(0, 0);
        byte p01 = img.GetPixel(0, 1);
        byte p10 = img.GetPixel(1, 0);
        byte p11 = img.GetPixel(1, 1);

        img.Invert();
        img.Invert();

        Assert.Equal(p00, img.GetPixel(0, 0));
        Assert.Equal(p01, img.GetPixel(0, 1));
        Assert.Equal(p10, img.GetPixel(1, 0));
        Assert.Equal(p11, img.GetPixel(1, 1));
    }

    // ---- Dimensions preserved ----

    [Fact]
    public void Invert_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P2, fill: 128);
        img.Invert();
        Assert.Equal(4, img.Height);
        Assert.Equal(6, img.Width);
    }

    // ---- Format preserved ----

    [Fact]
    public void Invert_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, fill: 200);
        img.Invert();
        Assert.Equal(NetpbmFormat.PGM_P2, img.Format);
    }

    // ---- PPM invert ----

    [Fact]
    public void Invert_PpmAllRed_BecomesAllCyan()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P3, fill: 0);
        // Set all pixels to red (R=255, G=0, B=0)
        for (int r = 0; r < 2; r++)
            for (int c = 0; c < 2; c++)
                img.SetPixelColor(r, c, 255, 0, 0);

        img.Invert();

        // After invert: R=0, G=255, B=255 (cyan)
        var (R, G, B) = img.GetPixelColor(0, 0);
        Assert.Equal(0,   R);
        Assert.Equal(255, G);
        Assert.Equal(255, B);
    }

    // ---- Dogfood: negative image pipeline ----

    [Fact]
    public void DogfoodPipeline_NegativeImage_HistogramMirrored()
    {
        // Create gradient: pixels 0, 64, 128, 192
        var img = NetpbmImage.Create(4, 1, NetpbmFormat.PGM_P2, fill: 0);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 64);
        img.SetPixel(0, 2, 128);
        img.SetPixel(0, 3, 192);

        img.Invert();

        // After invert: 255, 191, 127, 63
        Assert.Equal(255, img.GetPixel(0, 0));
        Assert.Equal(191, img.GetPixel(0, 1));
        Assert.Equal(127, img.GetPixel(0, 2));
        Assert.Equal(63,  img.GetPixel(0, 3));

        // Verify histogram: one pixel at each inverted value
        var hist = img.GetHistogram();
        Assert.Equal(1, hist[255]);
        Assert.Equal(1, hist[191]);
        Assert.Equal(1, hist[127]);
        Assert.Equal(1, hist[63]);
        Assert.Equal(4, hist.Sum()); // Total pixels
    }
}
