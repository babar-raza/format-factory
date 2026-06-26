// Tests for NetpbmImage.Invert, Solarize, ApplyGamma, Sharpen.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R160

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R160: Tests for NetpbmImage.Invert, Solarize, ApplyGamma, Sharpen.
/// Invert(): mutates pixels in-place; pixel p becomes MaxValue - p.
/// Solarize(threshold): pixels above threshold are inverted; below unchanged.
/// ApplyGamma(gamma): applies gamma correction; preserves dimensions.
/// Sharpen(): returns new sharpened image; same dimensions and format.
/// Covers: Invert changes pixels; Invert twice returns to original; Invert preserves dimensions;
/// Solarize threshold 0 inverts all; Solarize threshold 255 inverts none;
/// Solarize preserves dimensions; ApplyGamma 1.0 is identity-like;
/// ApplyGamma 2.0 changes pixels; Sharpen preserves dimensions; Sharpen preserves format;
/// dogfood Create->Invert->ApplyGamma->Sharpen->Solarize pipeline.
/// </summary>
public class NetpbmR160InvertSolarizeAndApplyGammaTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill = 128) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    // -------------------------------------------------------------------------
    // Invert
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_ChangesPixels()
    {
        var img = MakePgm(4, 4, 100);
        var before = img.GetPixel(0, 0);
        img.Invert();
        var after = img.GetPixel(0, 0);
        Assert.NotEqual(before, after);
    }

    [Fact]
    public void Invert_PixelBecomesMaxValueMinusOld()
    {
        var img = MakePgm(4, 4, 100);
        img.Invert();
        Assert.Equal(img.MaxValue - 100, img.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_Twice_ReturnsToOriginal()
    {
        var img = MakePgm(4, 4, 150);
        img.Invert();
        img.Invert();
        Assert.Equal(150, img.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_PreservesDimensions()
    {
        var img = MakePgm(5, 3, 80);
        img.Invert();
        Assert.Equal(5, img.Width);
        Assert.Equal(3, img.Height);
    }

    // -------------------------------------------------------------------------
    // Solarize
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_ThresholdZero_InvertsAllPixels()
    {
        var img = MakePgm(4, 4, 100);
        var result = img.Solarize(0);
        // threshold=0: all pixels > 0 get inverted -> 255 - 100 = 155
        Assert.Equal(img.MaxValue - 100, result.GetPixel(0, 0));
    }

    [Fact]
    public void Solarize_ThresholdMaxValue_PreservesPixels()
    {
        var img = MakePgm(4, 4, 100);
        var result = img.Solarize(255);
        // threshold=255: no pixels exceed 255, so none inverted
        Assert.Equal(100, result.GetPixel(0, 0));
    }

    [Fact]
    public void Solarize_PreservesDimensions()
    {
        var img = MakePgm(6, 4, 200);
        var result = img.Solarize(128);
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Solarize_BelowThreshold_Unchanged()
    {
        var img = MakePgm(4, 4, 50); // 50 < 128
        var result = img.Solarize(128);
        Assert.Equal(50, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // ApplyGamma
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_PreservesDimensions()
    {
        var img = MakePgm(5, 4, 128);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(5, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void ApplyGamma_One_IsApproximatelyIdentity()
    {
        var img = MakePgm(4, 4, 128);
        var result = img.ApplyGamma(1.0);
        // Gamma=1.0 should preserve pixel values approximately
        Assert.InRange(result.GetPixel(0, 0), (byte)120, (byte)135);
    }

    [Fact]
    public void ApplyGamma_Two_ChangesPixels()
    {
        var img = MakePgm(4, 4, 128);
        var original = img.GetPixel(0, 0);
        var result = img.ApplyGamma(2.0);
        // Gamma=2 darkens mid-range pixels
        Assert.NotEqual(original, result.GetPixel(0, 0));
    }

    [Fact]
    public void ApplyGamma_PreservesFormat()
    {
        var img = MakePgm(3, 3, 100);
        var result = img.ApplyGamma(1.5);
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
    }

    // -------------------------------------------------------------------------
    // Sharpen
    // -------------------------------------------------------------------------

    [Fact]
    public void Sharpen_PreservesDimensions()
    {
        var img = MakePgm(6, 6, 128);
        var result = img.Sharpen();
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Sharpen_PreservesFormat()
    {
        var img = MakePgm(4, 4, 100);
        var result = img.Sharpen();
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
    }

    [Fact]
    public void Sharpen_PixelCountMatchesDimensions()
    {
        var img = MakePgm(5, 4, 100);
        var result = img.Sharpen();
        Assert.Equal(result.Width * result.Height, result.Pixels.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Invert->ApplyGamma->Sharpen->Solarize
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InvertGammaSharpenSolarize_Pipeline()
    {
        var img = MakePgm(6, 6, 100);
        Assert.Equal(100, img.GetPixel(0, 0));

        // Invert
        img.Invert();
        Assert.Equal(155, img.GetPixel(0, 0)); // 255 - 100 = 155

        // ApplyGamma
        var gammaResult = img.ApplyGamma(1.0);
        Assert.Equal(6, gammaResult.Width);
        Assert.Equal(6, gammaResult.Height);

        // Sharpen
        var sharpened = gammaResult.Sharpen();
        Assert.Equal(6, sharpened.Width);
        Assert.Equal(6, sharpened.Height);
        Assert.Equal(NetpbmFormat.PGM_P2, sharpened.Format);

        // Solarize
        var solarized = sharpened.Solarize(128);
        Assert.Equal(6, solarized.Width);
        Assert.Equal(6, solarized.Height);
        Assert.Equal(36, solarized.Pixels.Length);
    }
}
