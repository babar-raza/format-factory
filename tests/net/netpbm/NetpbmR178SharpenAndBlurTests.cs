// Tests for NetpbmImage.Sharpen, BlurBox, MedianFilter.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R178

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R178: Tests for NetpbmImage.Sharpen, BlurBox, MedianFilter.
/// Sharpen(): applies an unsharp mask or sharpening kernel.
/// BlurBox(radius): applies box blur with given radius.
/// MedianFilter(radius): applies median filter with given radius.
/// Covers: Sharpen returns new image; Sharpen width unchanged; Sharpen height unchanged;
/// Sharpen pixels in valid range; BlurBox returns new image; BlurBox width unchanged;
/// BlurBox radius=1 dimensions unchanged; BlurBox on black image stays black;
/// BlurBox on white image stays white; MedianFilter returns new image;
/// MedianFilter dimensions unchanged; MedianFilter pixels in valid range;
/// BlurBox radius=2 still correct dimensions; Sharpen then GetStats mean in range;
/// dogfood Create->BlurBox->Sharpen->MedianFilter->GetStats pipeline.
/// </summary>
public class NetpbmR178SharpenAndBlurTests
{
    private static NetpbmImage CreateSolid(byte fill, int w = 6, int h = 6, NetpbmFormat fmt = NetpbmFormat.Pgm)
        => NetpbmImage.Create(w, h, fmt, fill);

    // -------------------------------------------------------------------------
    // Sharpen
    // -------------------------------------------------------------------------

    [Fact]
    public void Sharpen_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.Sharpen();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Sharpen_WidthUnchanged()
    {
        var img = CreateSolid(128, 6, 4);
        var result = img.Sharpen();
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void Sharpen_HeightUnchanged()
    {
        var img = CreateSolid(128, 6, 4);
        var result = img.Sharpen();
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Sharpen_PixelsInValidRange()
    {
        var img = CreateSolid(128);
        var result = img.Sharpen();
        var (_, min, max) = result.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
    }

    [Fact]
    public void Sharpen_ThenGetStats_MeanInRange()
    {
        var img = CreateSolid(100);
        var result = img.Sharpen();
        var (mean, _, _) = result.GetStats();
        Assert.InRange(mean, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // BlurBox
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.BlurBox(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurBox_WidthUnchanged()
    {
        var img = CreateSolid(128, 6, 4);
        var result = img.BlurBox(1);
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void BlurBox_Radius1_DimensionsUnchanged()
    {
        var img = CreateSolid(128, 6, 6);
        var result = img.BlurBox(1);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void BlurBox_OnBlackImage_StaysBlack()
    {
        var img = CreateSolid(0);
        var result = img.BlurBox(1);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(0.0, mean, 1);
    }

    [Fact]
    public void BlurBox_OnWhiteImage_StaysWhite()
    {
        var img = CreateSolid(255);
        var result = img.BlurBox(1);
        var (mean, _, _) = result.GetStats();
        Assert.Equal(255.0, mean, 1);
    }

    [Fact]
    public void BlurBox_Radius2_StillCorrectDimensions()
    {
        var img = CreateSolid(100, 8, 8);
        var result = img.BlurBox(2);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // MedianFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_ReturnsNewImage()
    {
        var img = CreateSolid(128);
        var result = img.MedianFilter(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MedianFilter_DimensionsUnchanged()
    {
        var img = CreateSolid(100, 6, 4);
        var result = img.MedianFilter(1);
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void MedianFilter_PixelsInValidRange()
    {
        var img = CreateSolid(150);
        var result = img.MedianFilter(1);
        var (_, min, max) = result.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->BlurBox->Sharpen->MedianFilter->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateBlurBoxSharpenMedianFilterGetStats_Pipeline()
    {
        // Create image with varied pixels
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.Pgm, 0);
        for (int r = 0; r < 6; r++)
        for (int c = 0; c < 6; c++)
            img.SetPixel(r, c, (byte)((r * c * 10) % 256));

        // BlurBox
        var blurred = img.BlurBox(1);
        Assert.Equal(6, blurred.Width);
        Assert.Equal(6, blurred.Height);
        var (_, blurMin, blurMax) = blurred.GetStats();
        Assert.True(blurMin >= 0 && blurMax <= 255);

        // Sharpen
        var sharpened = blurred.Sharpen();
        Assert.Equal(6, sharpened.Width);
        Assert.Equal(6, sharpened.Height);

        // MedianFilter
        var filtered = sharpened.MedianFilter(1);
        Assert.Equal(6, filtered.Width);
        Assert.Equal(6, filtered.Height);

        // GetStats
        var (mean, min, max) = filtered.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
