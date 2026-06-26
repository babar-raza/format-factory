// Tests for NetpbmImage.AdjustBrightness, AdjustContrast, Equalize, Threshold.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R176

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R176: Tests for NetpbmImage.AdjustBrightness, AdjustContrast, Equalize, Threshold.
/// AdjustBrightness(delta): shifts all pixel values by delta, clamped to [0,255].
/// AdjustContrast(factor): scales contrast around midpoint.
/// Equalize(): performs histogram equalization.
/// Threshold(t): binarizes image — pixels &gt;= t become 255, others 0.
/// Covers: AdjustBrightness +50 on black becomes 50; AdjustBrightness -50 on 100 becomes 50;
/// AdjustBrightness +300 on white stays 255 (clamped); AdjustBrightness returns new image;
/// AdjustBrightness width equals original; AdjustContrast returns new image;
/// AdjustContrast factor=1 unchanged; Equalize returns new image;
/// Equalize dimensions unchanged; Threshold all-black on high threshold;
/// Threshold all-white on zero threshold; Threshold on mid-gray;
/// AdjustBrightness then GetStats mean increases;
/// dogfood Create->AdjustBrightness->Threshold->GetStats pipeline.
/// </summary>
public class NetpbmR176AdjustBrightnessAndContrastTests
{
    private static NetpbmImage CreateSolid(byte fill, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, fill);

    // -------------------------------------------------------------------------
    // AdjustBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_PositiveDelta_BlackBecomesExpected()
    {
        var img = CreateSolid(0);
        var result = img.AdjustBrightness(50);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(50.0, mean, 0);
    }

    [Fact]
    public void AdjustBrightness_NegativeDelta_ReducesPixelValue()
    {
        var img = CreateSolid(100);
        var result = img.AdjustBrightness(-50);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(50.0, mean, 0);
    }

    [Fact]
    public void AdjustBrightness_LargeDelta_ClampedAt255()
    {
        var img = CreateSolid(255);
        var result = img.AdjustBrightness(300);
        var (_, _, max) = result.GetStats();
        Assert.Equal(255, max);
    }

    [Fact]
    public void AdjustBrightness_ReturnsNewImage()
    {
        var img = CreateSolid(100);
        var result = img.AdjustBrightness(10);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void AdjustBrightness_WidthEqualsOriginal()
    {
        var img = CreateSolid(100, 6, 3);
        var result = img.AdjustBrightness(10);
        Assert.Equal(img.Width, result.Width);
    }

    [Fact]
    public void AdjustBrightness_HeightEqualsOriginal()
    {
        var img = CreateSolid(100, 6, 3);
        var result = img.AdjustBrightness(10);
        Assert.Equal(img.Height, result.Height);
    }

    // -------------------------------------------------------------------------
    // AdjustContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.AdjustContrast(1.5);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void AdjustContrast_FactorOne_WidthUnchanged()
    {
        var img = CreateSolid(128, 5, 5);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Equalize
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.Equalize();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Equalize_DimensionsUnchanged()
    {
        var img = CreateSolid(128, 5, 3);
        var result = img.Equalize();
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    // -------------------------------------------------------------------------
    // Threshold
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_HighValue_AllBlack()
    {
        var img = CreateSolid(100);
        var result = img.Threshold(200); // all pixels < 200 → 0
        var (mean, _, _) = result.GetStats();
        Assert.Equal(0.0, mean, 0);
    }

    [Fact]
    public void Threshold_ZeroValue_AllWhite()
    {
        var img = CreateSolid(50);
        var result = img.Threshold(0); // all pixels >= 0 → 255
        var (mean, _, _) = result.GetStats();
        Assert.Equal(255.0, mean, 0);
    }

    [Fact]
    public void Threshold_ReturnsNewImage()
    {
        var img = CreateSolid(100);
        var result = img.Threshold(50);
        Assert.NotSame(img, result);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->AdjustBrightness->Threshold->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAdjustBrightnessThresholdGetStats_Pipeline()
    {
        // Create mid-gray image
        var img = CreateSolid(100, 4, 4);

        // AdjustBrightness +30 → 130
        var bright = img.AdjustBrightness(30);
        var (bmean, _, _) = bright.GetStats();
        Assert.Equal(130.0, bmean, 0);
        Assert.Equal(img.Width, bright.Width);
        Assert.Equal(img.Height, bright.Height);

        // Threshold at 128 → all 255 (since 130 >= 128)
        var binary = bright.Threshold(128);
        var (tmean, tmin, tmax) = binary.GetStats();
        Assert.Equal(255.0, tmean, 0);
        Assert.Equal(255, tmin);
        Assert.Equal(255, tmax);

        // GetBrightness should be 1.0 (all white)
        var brightness = binary.GetBrightness();
        Assert.Equal(1.0, brightness, 3);
    }
}
