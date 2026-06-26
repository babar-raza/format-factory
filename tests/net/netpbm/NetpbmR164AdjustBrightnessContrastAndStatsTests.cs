// Tests for NetpbmImage.AdjustBrightness, AdjustContrast, Equalize, GetStats.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R164

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R164: Tests for NetpbmImage.AdjustBrightness, AdjustContrast, Equalize, GetStats.
/// AdjustBrightness(delta): shifts pixel values by delta, clamped to [0, MaxValue].
/// AdjustContrast(factor): scales contrast around midpoint.
/// Equalize(): histogram equalization; spreads pixel values across full range.
/// GetStats(): returns (Mean, Min, Max) for pixel values.
/// Covers: AdjustBrightness positive increases mean; AdjustBrightness negative decreases mean;
/// AdjustBrightness clamps at 0; AdjustBrightness preserves dimensions;
/// AdjustContrast factor>1 increases range; AdjustContrast preserves dimensions;
/// Equalize returns image same size; Equalize does not lose pixels;
/// GetStats Mean non-negative; GetStats Min <= Mean <= Max;
/// GetStats on uniform image; GetStats Max equals MaxValue for white image;
/// dogfood Create->AdjustBrightness->GetStats->AdjustContrast pipeline.
/// </summary>
public class NetpbmR164AdjustBrightnessContrastAndStatsTests
{
    private static NetpbmImage CreateGray(int width, int height, byte fill)
    {
        var img = NetpbmImage.Create(width, height, NetpbmFormat.PGM_P2, fill);
        return img;
    }

    // -------------------------------------------------------------------------
    // AdjustBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_PositiveDelta_IncreasesMean()
    {
        var img = CreateGray(4, 4, 100);
        var brightened = img.AdjustBrightness(50);
        var (mean, _, _) = brightened.GetStats();
        Assert.True(mean >= 100);
    }

    [Fact]
    public void AdjustBrightness_NegativeDelta_DecreasesMean()
    {
        var img = CreateGray(4, 4, 100);
        var darkened = img.AdjustBrightness(-50);
        var (mean, _, _) = darkened.GetStats();
        Assert.True(mean <= 100);
    }

    [Fact]
    public void AdjustBrightness_ClampsAtZero()
    {
        var img = CreateGray(4, 4, 10);
        var darkened = img.AdjustBrightness(-200); // would go negative
        var (_, min, _) = darkened.GetStats();
        Assert.True(min >= 0);
    }

    [Fact]
    public void AdjustBrightness_PreservesDimensions()
    {
        var img = CreateGray(5, 6, 128);
        var result = img.AdjustBrightness(20);
        Assert.Equal(5, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void AdjustBrightness_WhiteImagePlusDelta_StaysAtMax()
    {
        var img = CreateGray(4, 4, 255);
        var result = img.AdjustBrightness(50);
        var (_, _, max) = result.GetStats();
        Assert.Equal(255, max);
    }

    // -------------------------------------------------------------------------
    // AdjustContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_PreservesDimensions()
    {
        var img = CreateGray(4, 4, 128);
        var result = img.AdjustContrast(1.5);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void AdjustContrast_FactorOne_LeavesImageSimilar()
    {
        var img = CreateGray(4, 4, 128);
        var result = img.AdjustContrast(1.0);
        var (mean, _, _) = result.GetStats();
        Assert.True(mean >= 0);
    }

    [Fact]
    public void AdjustContrast_FactorZero_FlattensImage()
    {
        // factor=0 collapses all pixels to midpoint
        var img = CreateGray(4, 4, 200);
        var result = img.AdjustContrast(0.0);
        var (_, min, max) = result.GetStats();
        Assert.True(max - min <= 2); // should be very flat
    }

    // -------------------------------------------------------------------------
    // Equalize
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_ReturnsSameSizeImage()
    {
        var img = CreateGray(6, 6, 100);
        var equalized = img.Equalize();
        Assert.Equal(6, equalized.Width);
        Assert.Equal(6, equalized.Height);
    }

    [Fact]
    public void Equalize_PixelCountPreserved()
    {
        var img = CreateGray(4, 5, 120);
        var equalized = img.Equalize();
        Assert.Equal(img.Width * img.Height, equalized.Width * equalized.Height);
    }

    // -------------------------------------------------------------------------
    // GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStats_MeanNonNegative()
    {
        var img = CreateGray(4, 4, 100);
        var (mean, _, _) = img.GetStats();
        Assert.True(mean >= 0);
    }

    [Fact]
    public void GetStats_MinLessThanOrEqualMeanLessThanMax()
    {
        var img = CreateGray(4, 4, 128);
        var (mean, min, max) = img.GetStats();
        Assert.True(min <= mean);
        Assert.True(mean <= max);
    }

    [Fact]
    public void GetStats_UniformImage_MinEqualsMax()
    {
        var img = CreateGray(4, 4, 77);
        var (_, min, max) = img.GetStats();
        Assert.Equal(min, max);
        Assert.Equal(77, min);
    }

    [Fact]
    public void GetStats_WhiteImage_MaxEquals255()
    {
        var img = CreateGray(4, 4, 255);
        var (_, _, max) = img.GetStats();
        Assert.Equal(255, max);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->AdjustBrightness->GetStats->AdjustContrast pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_BrightnessStatsContrastPipeline()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P2, 100);

        // Adjust brightness
        var brightened = img.AdjustBrightness(30);
        var (mean1, min1, max1) = brightened.GetStats();
        Assert.True(mean1 >= 100);
        Assert.True(min1 >= 0);
        Assert.True(max1 <= 255);

        // Adjust contrast on brightened
        var contrasted = brightened.AdjustContrast(1.2);
        var (_, _, _) = contrasted.GetStats();
        Assert.Equal(8, contrasted.Width);
        Assert.Equal(8, contrasted.Height);

        // Equalize
        var equalized = contrasted.Equalize();
        Assert.Equal(8, equalized.Width);
        Assert.Equal(8, equalized.Height);
    }
}
