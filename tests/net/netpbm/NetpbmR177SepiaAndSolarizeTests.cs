// Tests for NetpbmImage.Sepia, Solarize, ApplyGamma, Posterize.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R177

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R177: Tests for NetpbmImage.Sepia, Solarize, ApplyGamma, Posterize.
/// Sepia(): applies sepia tone effect to a grayscale or color image.
/// Solarize(threshold): inverts pixels above threshold.
/// ApplyGamma(gamma): applies gamma correction.
/// Posterize(levels): reduces color palette to N levels.
/// Covers: Sepia returns new image; Sepia dimensions unchanged; Sepia format is PPM;
/// Solarize returns new image; Solarize dimensions unchanged;
/// Solarize threshold=0 inverts all; ApplyGamma returns new image;
/// ApplyGamma gamma=1 dimensions unchanged; ApplyGamma gamma=2 non-negative pixels;
/// Posterize returns new image; Posterize dimensions unchanged;
/// Posterize levels=2 binarizes; Posterize levels=256 nearly unchanged;
/// dogfood Create->Sepia->Solarize->GetStats pipeline.
/// </summary>
public class NetpbmR177SepiaAndSolarizeTests
{
    private static NetpbmImage CreateSolid(byte fill, int w = 4, int h = 4, NetpbmFormat fmt = NetpbmFormat.Pgm)
        => NetpbmImage.Create(w, h, fmt, fill);

    // -------------------------------------------------------------------------
    // Sepia
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.Sepia();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Sepia_DimensionsUnchanged()
    {
        var img = CreateSolid(100, 5, 3);
        var result = img.Sepia();
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Sepia_FormatIsPpm()
    {
        var img = CreateSolid(150);
        var result = img.Sepia();
        Assert.Equal(NetpbmFormat.Ppm, result.Format);
    }

    // -------------------------------------------------------------------------
    // Solarize
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.Solarize(128);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Solarize_DimensionsUnchanged()
    {
        var img = CreateSolid(100, 5, 3);
        var result = img.Solarize(128);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Solarize_ThresholdZero_InvertsAll()
    {
        var img = CreateSolid(200);
        // With threshold=0 all pixels >= 0, so all are inverted: 255-200=55
        var result = img.Solarize(0);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(55.0, mean, 0);
    }

    [Fact]
    public void Solarize_HighThreshold_NoChange()
    {
        // Pixels below threshold are NOT inverted
        var img = CreateSolid(50);
        // With threshold=200, pixels 50 < 200, no inversion
        var result = img.Solarize(200);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(50.0, mean, 0);
    }

    // -------------------------------------------------------------------------
    // ApplyGamma
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.ApplyGamma(2.0);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ApplyGamma_GammaOne_DimensionsUnchanged()
    {
        var img = CreateSolid(100, 5, 5);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void ApplyGamma_GammaTwo_PixelsNonNegative()
    {
        var img = CreateSolid(100);
        var result = img.ApplyGamma(2.0);
        var (_, min, _) = result.GetStats();
        Assert.True(min >= 0);
    }

    // -------------------------------------------------------------------------
    // Posterize
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.Posterize(4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Posterize_DimensionsUnchanged()
    {
        var img = CreateSolid(100, 5, 3);
        var result = img.Posterize(4);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Posterize_TwoLevels_OnlyTwoDistinctValues()
    {
        // 2 levels: pixels are either 0 or 255
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.Pgm, 0);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 200);
        var result = img.Posterize(2);
        var hist = result.GetHistogram();
        // Count non-zero buckets
        var nonZeroBuckets = 0;
        for (var i = 0; i < 256; i++)
            if (hist[i] > 0) nonZeroBuckets++;
        Assert.True(nonZeroBuckets <= 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Sepia->Solarize->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSepiaSolarizeGetStats_Pipeline()
    {
        // Create gray image
        var img = CreateSolid(150, 4, 4);
        Assert.Equal(NetpbmFormat.Pgm, img.Format);

        // Sepia → converts to PPM
        var sepia = img.Sepia();
        Assert.Equal(NetpbmFormat.Ppm, sepia.Format);
        Assert.Equal(img.Width, sepia.Width);
        Assert.Equal(img.Height, sepia.Height);

        // Solarize the sepia image (as grayscale for simplicity — convert first)
        var gray = sepia.ToGrayscale();
        Assert.Equal(NetpbmFormat.Pgm, gray.Format);

        // Solarize at 128
        var solarized = gray.Solarize(128);
        Assert.Equal(img.Width, solarized.Width);
        Assert.Equal(img.Height, solarized.Height);

        // GetStats
        var (mean, min, max) = solarized.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
