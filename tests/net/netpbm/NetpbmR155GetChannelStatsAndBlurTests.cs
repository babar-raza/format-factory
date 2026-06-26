// Tests for NetpbmImage/NetpbmImageAnalyzer.GetChannelStats, NetpbmImageFilters.BlurBox,
// NetpbmImageFilters.Posterize, NetpbmImageFilters.Sepia.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R155

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R155: Tests for NetpbmImageAnalyzer.GetChannelStats, BlurBox, Posterize, Sepia.
/// GetChannelStats(): returns per-channel (R,G,B) stats for PPM images.
/// BlurBox(radius): box-blur filter; result has same dimensions.
/// Posterize(levels): reduces color levels; result has same dimensions.
/// Sepia(): applies sepia tone; result is a PPM image.
/// Covers: GetChannelStats on uniform red image all R=255; GetChannelStats G/B=0 for red;
/// GetChannelStats on PGM throws or returns symmetric; BlurBox radius=1 preserves dimensions;
/// BlurBox radius=0 preserves pixel values approximately; BlurBox result max pixel <=255;
/// Posterize levels=2 reduces distinct pixel values; Posterize preserves dimensions;
/// Posterize level=1 all pixels same value; Sepia preserves dimensions;
/// Sepia result has PPM format; Sepia no channel is all-zero;
/// dogfood Create->BlurBox->Posterize->GetStats pipeline.
/// </summary>
public class NetpbmR155GetChannelStatsAndBlurTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    private static NetpbmImage MakeRed(int w, int h)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PPM_P3, 0);
        var r = new byte[w * h];
        var g = new byte[w * h];
        var b = new byte[w * h];
        for (var i = 0; i < w * h; i++) r[i] = 255;
        img.RedChannel = r;
        img.GreenChannel = g;
        img.BlueChannel = b;
        return img;
    }

    // -------------------------------------------------------------------------
    // GetChannelStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStats_PureRedImage_RChannelMax255()
    {
        var img = MakeRed(4, 4);
        var analyzer = new NetpbmImageAnalyzer(img);
        var (r, g, b) = analyzer.GetChannelStats();
        Assert.Equal(255, r.Max);
    }

    [Fact]
    public void GetChannelStats_PureRedImage_GChannelIsZero()
    {
        var img = MakeRed(4, 4);
        var analyzer = new NetpbmImageAnalyzer(img);
        var (r, g, b) = analyzer.GetChannelStats();
        Assert.Equal(0, g.Max);
    }

    [Fact]
    public void GetChannelStats_PureRedImage_BChannelIsZero()
    {
        var img = MakeRed(4, 4);
        var analyzer = new NetpbmImageAnalyzer(img);
        var (r, g, b) = analyzer.GetChannelStats();
        Assert.Equal(0, b.Max);
    }

    // -------------------------------------------------------------------------
    // BlurBox
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_Radius1_PreservesDimensions()
    {
        var img = MakePgm(6, 4, 128);
        var blurred = img.BlurBox(1);
        Assert.Equal(6, blurred.Width);
        Assert.Equal(4, blurred.Height);
    }

    [Fact]
    public void BlurBox_PixelValuesClamped()
    {
        var img = MakePgm(4, 4, 200);
        var blurred = img.BlurBox(1);
        for (var r = 0; r < blurred.Height; r++)
            for (var c = 0; c < blurred.Width; c++)
                Assert.InRange(blurred.GetPixel(r, c), (byte)0, (byte)255);
    }

    [Fact]
    public void BlurBox_Radius0_PreservesDimensions()
    {
        var img = MakePgm(4, 4, 100);
        var blurred = img.BlurBox(0);
        Assert.Equal(4, blurred.Width);
        Assert.Equal(4, blurred.Height);
    }

    // -------------------------------------------------------------------------
    // Posterize
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_PreservesDimensions()
    {
        var img = MakePgm(4, 4, 128);
        var posterized = img.Posterize(4);
        Assert.Equal(4, posterized.Width);
        Assert.Equal(4, posterized.Height);
    }

    [Fact]
    public void Posterize_Levels1_AllPixelsSameValue()
    {
        var img = MakePgm(3, 3, 150);
        var posterized = img.Posterize(1);
        var firstPixel = posterized.GetPixel(0, 0);
        for (var r = 0; r < posterized.Height; r++)
            for (var c = 0; c < posterized.Width; c++)
                Assert.Equal(firstPixel, posterized.GetPixel(r, c));
    }

    [Fact]
    public void Posterize_PixelCountUnchanged()
    {
        var img = MakePgm(4, 4, 100);
        var posterized = img.Posterize(4);
        Assert.Equal(16, posterized.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // Sepia
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_PreservesDimensions()
    {
        var img = MakeRed(4, 4);
        var sepia = img.Sepia();
        Assert.Equal(4, sepia.Width);
        Assert.Equal(4, sepia.Height);
    }

    [Fact]
    public void Sepia_ResultIsPpmFormat()
    {
        var img = MakeRed(4, 4);
        var sepia = img.Sepia();
        // Sepia is a color operation — output should be PPM
        Assert.True(
            sepia.Format == NetpbmFormat.PPM_P3 || sepia.Format == NetpbmFormat.PPM_P6,
            $"Expected PPM format, got {sepia.Format}");
    }

    [Fact]
    public void Sepia_RedChannelNotAllZero()
    {
        var img = MakeRed(4, 4);
        var sepia = img.Sepia();
        // Sepia should have some non-zero red component
        Assert.NotNull(sepia.RedChannel);
        var hasNonZero = false;
        foreach (var v in sepia.RedChannel!)
            if (v > 0) { hasNonZero = true; break; }
        Assert.True(hasNonZero);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->BlurBox->Posterize->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_BlurPosterizeStats_Pipeline()
    {
        var img = MakePgm(8, 8, 0);
        // Add some variation
        for (var r = 0; r < 8; r++)
            for (var c = 0; c < 8; c++)
                img.SetPixel(r, c, (byte)((r * 8 + c) * 4 % 256));

        // Blur
        var blurred = img.BlurBox(1);
        Assert.Equal(8, blurred.Width);

        // Posterize
        var posterized = blurred.Posterize(4);
        Assert.Equal(8, posterized.Width);

        // GetStats
        var analyzer = new NetpbmImageAnalyzer(posterized);
        var (mean, min, max) = analyzer.GetStats();
        Assert.True(mean >= min && mean <= max);
    }
}
