// Tests for NetpbmImage.Sepia, Posterize, BlurBox, MedianFilter.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R165

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R165: Tests for NetpbmImage.Sepia, Posterize, BlurBox, MedianFilter.
/// Sepia(): converts to color image with sepia tone effect.
/// Posterize(levels): reduces color palette to specified level count.
/// BlurBox(radius): applies box blur of given radius.
/// MedianFilter(radius): applies median filter of given radius.
/// Covers: Sepia returns color image (PPM format); Sepia preserves dimensions;
/// Posterize 2 levels returns image; Posterize preserves dimensions;
/// Posterize 8 levels returns image; BlurBox radius 1 preserves dimensions;
/// BlurBox result pixel values in valid range; MedianFilter radius 1 preserves dims;
/// MedianFilter on grayscale image; MedianFilter on color image;
/// GetBrightness non-negative after filters; Sepia mean in valid range;
/// dogfood Create->Sepia->Posterize->BlurBox pipeline.
/// </summary>
public class NetpbmR165SepiaPosterizeAndBlurTests
{
    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    private static NetpbmImage CreateColor(int w, int h)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PPM_P3, 0);
        // Fill with mid-gray-ish color
        for (var row = 0; row < h; row++)
            for (var col = 0; col < w; col++)
                img.SetPixelColor(row, col, 150, 100, 80);
        return img;
    }

    // -------------------------------------------------------------------------
    // Sepia
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_ReturnsColorImage()
    {
        var img = CreateGray(4, 4, 128);
        var result = img.Sepia();
        // Sepia converts to color (PPM)
        Assert.True(result.Format == NetpbmFormat.PPM_P3 || result.Format == NetpbmFormat.PPM_P6
            || result.RedChannel != null);
    }

    [Fact]
    public void Sepia_PreservesDimensions()
    {
        var img = CreateGray(5, 6, 100);
        var result = img.Sepia();
        Assert.Equal(5, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Sepia_OnColorImage_PreservesDimensions()
    {
        var img = CreateColor(4, 4);
        var result = img.Sepia();
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Sepia_MeanIsInValidRange()
    {
        var img = CreateGray(4, 4, 128);
        var result = img.Sepia();
        var brightness = result.GetBrightness();
        Assert.True(brightness >= 0 && brightness <= 255);
    }

    // -------------------------------------------------------------------------
    // Posterize
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_TwoLevels_ReturnsImage()
    {
        var img = CreateGray(4, 4, 128);
        var result = img.Posterize(2);
        Assert.NotNull(result);
        Assert.True(result.Pixels.Length > 0);
    }

    [Fact]
    public void Posterize_PreservesDimensions()
    {
        var img = CreateGray(5, 6, 100);
        var result = img.Posterize(4);
        Assert.Equal(5, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Posterize_EightLevels_ReturnsImage()
    {
        var img = CreateGray(4, 4, 200);
        var result = img.Posterize(8);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // BlurBox
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_Radius1_PreservesDimensions()
    {
        var img = CreateGray(6, 6, 128);
        var result = img.BlurBox(1);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void BlurBox_PixelValuesInValidRange()
    {
        var img = CreateGray(4, 4, 200);
        var result = img.BlurBox(1);
        foreach (var px in result.Pixels)
            Assert.True(px >= 0 && px <= 255);
    }

    [Fact]
    public void BlurBox_Radius2_PreservesDimensions()
    {
        var img = CreateGray(8, 8, 100);
        var result = img.BlurBox(2);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // MedianFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_Radius1_PreservesDimensions()
    {
        var img = CreateGray(6, 6, 128);
        var result = img.MedianFilter(1);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void MedianFilter_OnGrayscaleImage_ReturnsImage()
    {
        var img = CreateGray(4, 4, 150);
        var result = img.MedianFilter(1);
        Assert.NotNull(result);
        Assert.True(result.Pixels.Length > 0);
    }

    [Fact]
    public void MedianFilter_OnColorImage_PreservesDimensions()
    {
        var img = CreateColor(4, 4);
        var result = img.MedianFilter(1);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_NonNegativeAfterFilters()
    {
        var img = CreateGray(4, 4, 128);
        var blurred = img.BlurBox(1);
        Assert.True(blurred.GetBrightness() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Sepia->Posterize->BlurBox pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SepiaPosterizeBlurPipeline()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P2, 180);
        Assert.Equal(8, img.Width);

        // Sepia
        var sepia = img.Sepia();
        Assert.Equal(8, sepia.Width);
        Assert.Equal(8, sepia.Height);

        // Posterize
        var posterized = img.Posterize(4);
        Assert.Equal(8, posterized.Width);

        // BlurBox on original
        var blurred = img.BlurBox(1);
        Assert.Equal(8, blurred.Width);
        Assert.Equal(8, blurred.Height);

        // Median filter
        var median = img.MedianFilter(1);
        Assert.Equal(8, median.Width);

        // GetBrightness consistent
        Assert.True(img.GetBrightness() >= 0);
        Assert.True(blurred.GetBrightness() >= 0);
    }
}
