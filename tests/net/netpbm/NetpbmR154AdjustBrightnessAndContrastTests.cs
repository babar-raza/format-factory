// Tests for NetpbmImage.AdjustBrightness, AdjustContrast, Equalize, GetStats.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R154

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R154: Tests for NetpbmImage.AdjustBrightness, AdjustContrast, Equalize, GetStats.
/// AdjustBrightness(delta): clamps each pixel by delta; positive brightens, negative darkens.
/// AdjustContrast(factor): scales distance from 128; factor > 1 increases contrast.
/// Equalize(): histogram equalization — spreads intensity distribution.
/// GetStats(): returns (Mean, Min, Max) over all pixels.
/// Covers: AdjustBrightness positive delta raises pixels; AdjustBrightness negative delta lowers;
/// AdjustBrightness clamps at 255; AdjustBrightness clamps at 0; AdjustBrightness preserves dimensions;
/// AdjustContrast factor=1.0 preserves values approximately; AdjustContrast preserves dimensions;
/// Equalize preserves dimensions; Equalize pixel count unchanged;
/// GetStats Mean is between Min and Max; GetStats Min <= Max;
/// dogfood Create->AdjustBrightness->AdjustContrast->GetStats pipeline.
/// </summary>
public class NetpbmR154AdjustBrightnessAndContrastTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    private static NetpbmImage MakeGradient(int w, int h)
    {
        var img = MakePgm(w, h, 0);
        for (var r = 0; r < h; r++)
            for (var c = 0; c < w; c++)
                img.SetPixel(r, c, (byte)((r * w + c) % 256));
        return img;
    }

    // -------------------------------------------------------------------------
    // AdjustBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_PositiveDelta_RaisesPixels()
    {
        var img = MakePgm(2, 2, 100);
        var bright = img.AdjustBrightness(50);
        Assert.Equal(150, bright.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustBrightness_NegativeDelta_LowersPixels()
    {
        var img = MakePgm(2, 2, 100);
        var dark = img.AdjustBrightness(-50);
        Assert.Equal(50, dark.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustBrightness_ClampsAt255()
    {
        var img = MakePgm(2, 2, 250);
        var bright = img.AdjustBrightness(100);
        Assert.Equal(255, bright.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustBrightness_ClampsAt0()
    {
        var img = MakePgm(2, 2, 20);
        var dark = img.AdjustBrightness(-100);
        Assert.Equal(0, dark.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustBrightness_PreservesDimensions()
    {
        var img = MakePgm(4, 3, 128);
        var result = img.AdjustBrightness(10);
        Assert.Equal(4, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void AdjustBrightness_ZeroDelta_SameValues()
    {
        var img = MakePgm(2, 2, 100);
        var result = img.AdjustBrightness(0);
        Assert.Equal(100, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // AdjustContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_PreservesDimensions()
    {
        var img = MakeGradient(4, 4);
        var result = img.AdjustContrast(1.5);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void AdjustContrast_FactorOne_ApproximatelyPreservesValues()
    {
        var img = MakePgm(2, 2, 128);
        var result = img.AdjustContrast(1.0);
        // Pixel at 128 is the center — factor=1 should leave it close to 128
        Assert.InRange(result.GetPixel(0, 0), (byte)125, (byte)131);
    }

    [Fact]
    public void AdjustContrast_PixelCountMatchesDimensions()
    {
        var img = MakeGradient(3, 3);
        var result = img.AdjustContrast(2.0);
        Assert.Equal(result.Width * result.Height, result.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // Equalize
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_PreservesDimensions()
    {
        var img = MakeGradient(8, 8);
        var eq = img.Equalize();
        Assert.Equal(8, eq.Width);
        Assert.Equal(8, eq.Height);
    }

    [Fact]
    public void Equalize_PixelCountUnchanged()
    {
        var img = MakeGradient(4, 4);
        var eq = img.Equalize();
        Assert.Equal(16, eq.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_MeanBetweenMinAndMax()
    {
        var img = MakeGradient(4, 4);
        var analyzer = new NetpbmImageAnalyzer(img);
        var (mean, min, max) = analyzer.GetStats();
        Assert.True(mean >= min && mean <= max,
            $"Mean={mean} not in [{min},{max}]");
    }

    [Fact]
    public void GetStats_MinLessThanOrEqualMax()
    {
        var img = MakeGradient(4, 4);
        var analyzer = new NetpbmImageAnalyzer(img);
        var (_, min, max) = analyzer.GetStats();
        Assert.True(min <= max);
    }

    [Fact]
    public void GetStats_UniformImage_MinEqualsMax()
    {
        var img = MakePgm(3, 3, 77);
        var analyzer = new NetpbmImageAnalyzer(img);
        var (mean, min, max) = analyzer.GetStats();
        Assert.Equal(77, min);
        Assert.Equal(77, max);
        Assert.Equal(77.0, mean, precision: 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->AdjustBrightness->AdjustContrast->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_BrightnessContrastStats_Pipeline()
    {
        var img = MakeGradient(8, 8);

        // Brighten then check stats
        var bright = img.AdjustBrightness(20);
        var analyzerB = new NetpbmImageAnalyzer(bright);
        var (meanB, minB, maxB) = analyzerB.GetStats();
        Assert.True(minB >= 0 && maxB <= 255);

        // Adjust contrast and check dims
        var contrasted = bright.AdjustContrast(1.5);
        Assert.Equal(8, contrasted.Width);
        Assert.Equal(8, contrasted.Height);

        // Stats on contrasted
        var analyzerC = new NetpbmImageAnalyzer(contrasted);
        var (meanC, minC, maxC) = analyzerC.GetStats();
        Assert.True(meanC >= minC && meanC <= maxC);
    }
}
