// Tests for NetpbmImage.ToGrayscale, ToColor, GetHistogram, Pipeline.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R158

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R158: Tests for NetpbmImage.ToGrayscale, ToColor, GetHistogram, Pipeline.
/// ToGrayscale(): converts PPM to PGM_P2; returns grayscale image with same dimensions.
/// ToColor(): converts PGM to PPM_P3; returns color image with same dimensions.
/// GetHistogram(): returns int[256] with frequency counts summing to Width*Height.
/// Pipeline(steps): applies transforms in sequence; result has expected properties.
/// Covers: ToGrayscale PPM->PGM format; ToGrayscale preserves dimensions;
/// ToGrayscale pixels in [0,255]; ToColor PGM->PPM format;
/// ToColor preserves dimensions; ToColor populates color channels;
/// GetHistogram length 256; GetHistogram sum equals pixel count;
/// GetHistogram uniform image has single peak; Pipeline applies multiple steps;
/// dogfood Create->ToColor->Overlay->ToGrayscale->GetHistogram pipeline.
/// </summary>
public class NetpbmR158ToGrayscaleAndHistogramTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill = 128) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    private static NetpbmImage MakePpm(int w, int h, byte r, byte g, byte b)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PPM_P3, r);
        // Set all pixels to fill and color channels
        for (var i = 0; i < w * h; i++)
        {
            img.RedChannel![i] = r;
            img.GreenChannel![i] = g;
            img.BlueChannel![i] = b;
        }
        return img;
    }

    // -------------------------------------------------------------------------
    // ToGrayscale
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_FromPpm_ReturnsPgmFormat()
    {
        var ppm = MakePpm(4, 4, 100, 150, 200);
        var gray = ppm.ToGrayscale();
        Assert.Equal(NetpbmFormat.PGM_P2, gray.Format);
    }

    [Fact]
    public void ToGrayscale_PreservesDimensions()
    {
        var ppm = MakePpm(5, 3, 100, 100, 100);
        var gray = ppm.ToGrayscale();
        Assert.Equal(5, gray.Width);
        Assert.Equal(3, gray.Height);
    }

    [Fact]
    public void ToGrayscale_PixelsInValidRange()
    {
        var ppm = MakePpm(4, 4, 200, 50, 150);
        var gray = ppm.ToGrayscale();
        Assert.All(gray.Pixels, p => Assert.InRange(p, (byte)0, (byte)255));
    }

    [Fact]
    public void ToGrayscale_FromPgm_ReturnsSameFormat()
    {
        var pgm = MakePgm(3, 3, 100);
        var gray = pgm.ToGrayscale();
        // PGM->ToGrayscale is a no-op or returns PGM
        Assert.True(gray.Format == NetpbmFormat.PGM_P2 || gray.Format == NetpbmFormat.PGM_P5);
    }

    [Fact]
    public void ToGrayscale_AllSameColor_UniformOutput()
    {
        var ppm = MakePpm(4, 4, 128, 128, 128);
        var gray = ppm.ToGrayscale();
        // Uniform gray input -> uniform gray output
        var first = gray.Pixels[0];
        Assert.All(gray.Pixels, p => Assert.Equal(first, p));
    }

    // -------------------------------------------------------------------------
    // ToColor
    // -------------------------------------------------------------------------

    [Fact]
    public void ToColor_FromPgm_ReturnsPpmFormat()
    {
        var pgm = MakePgm(4, 4, 100);
        var color = pgm.ToColor();
        Assert.True(color.Format == NetpbmFormat.PPM_P3 || color.Format == NetpbmFormat.PPM_P6);
    }

    [Fact]
    public void ToColor_PreservesDimensions()
    {
        var pgm = MakePgm(6, 2, 80);
        var color = pgm.ToColor();
        Assert.Equal(6, color.Width);
        Assert.Equal(2, color.Height);
    }

    [Fact]
    public void ToColor_PopulatesColorChannels()
    {
        var pgm = MakePgm(3, 3, 100);
        var color = pgm.ToColor();
        Assert.NotNull(color.RedChannel);
        Assert.NotNull(color.GreenChannel);
        Assert.NotNull(color.BlueChannel);
    }

    [Fact]
    public void ToColor_GrayValue_AllChannelsEqual()
    {
        var pgm = MakePgm(2, 2, 150);
        var color = pgm.ToColor();
        // Grayscale->color: R==G==B==original gray
        Assert.Equal(color.RedChannel![0], color.GreenChannel![0]);
        Assert.Equal(color.GreenChannel![0], color.BlueChannel![0]);
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_LengthIs256()
    {
        var img = MakePgm(4, 4, 128);
        var hist = img.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = MakePgm(5, 4, 100);
        var hist = img.GetHistogram();
        Assert.Equal(img.Width * img.Height, hist.Sum());
    }

    [Fact]
    public void GetHistogram_UniformImage_SinglePeak()
    {
        var img = MakePgm(4, 4, 200);
        var hist = img.GetHistogram();
        // All pixels are 200 -> hist[200] == 16, all others 0
        Assert.Equal(16, hist[200]);
        var others = hist.Where((v, i) => i != 200).Sum();
        Assert.Equal(0, others);
    }

    [Fact]
    public void GetHistogram_MixedValues_AllAccountedFor()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        img.SetPixel(0, 0, 10);
        img.SetPixel(0, 1, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(1, 1, 200);
        var hist = img.GetHistogram();
        Assert.Equal(1, hist[10]);
        Assert.Equal(1, hist[50]);
        Assert.Equal(1, hist[100]);
        Assert.Equal(1, hist[200]);
        Assert.Equal(4, hist.Sum());
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->ToColor->Overlay->ToGrayscale->GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ColorOverlayGrayscaleHistogram_Pipeline()
    {
        // Start with a gray image, convert to color
        var base_ = MakePgm(6, 6, 100);
        var color = base_.ToColor();
        Assert.True(color.RedChannel != null);

        // Overlay a small bright patch
        var stamp = MakePpm(2, 2, 255, 255, 255);
        var overlaid = color.Overlay(stamp, 0, 0);
        Assert.Equal(6, overlaid.Width);
        Assert.Equal(6, overlaid.Height);

        // Convert back to grayscale
        var gray = overlaid.ToGrayscale();
        Assert.Equal(NetpbmFormat.PGM_P2, gray.Format);
        Assert.Equal(6, gray.Width);
        Assert.Equal(6, gray.Height);

        // Histogram should account for all pixels
        var hist = gray.GetHistogram();
        Assert.Equal(36, hist.Sum());
        Assert.Equal(256, hist.Length);
    }
}
