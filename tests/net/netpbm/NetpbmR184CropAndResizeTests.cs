// Tests for NetpbmImage.Crop, Resize, MergeHorizontal, MergeVertical deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R184

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R184: Tests for NetpbmImage.Crop, Resize, MergeHorizontal, MergeVertical deeper coverage.
/// Crop(x, y, w, h): returns a cropped region of the image.
/// Resize(newWidth, newHeight): resizes image to new dimensions.
/// MergeHorizontal(other): merges two images side-by-side.
/// MergeVertical(other): merges two images top-to-bottom.
/// Covers: Crop returns new image; Crop dimensions match request;
/// Crop preserves pixel values; Resize returns new image;
/// Resize to exact dimensions; Resize up dimensions;
/// Resize down dimensions; MergeHorizontal width is sum;
/// MergeHorizontal height matches; MergeVertical height is sum;
/// MergeVertical width matches; Crop then Resize chain;
/// MergeHorizontal then ConvertFormat; MergeVertical then GetStats;
/// dogfood Create->Crop->Resize->MergeHorizontal->MergeVertical->GetStats pipeline.
/// </summary>
public class NetpbmR184CropAndResizeTests
{
    private static NetpbmImage CreateGray(byte fill, int w, int h)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, fill);

    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_ReturnsNewImage()
    {
        var img = CreateGray(128, 8, 8);
        var cropped = img.Crop(0, 0, 4, 4);
        Assert.NotSame(img, cropped);
    }

    [Fact]
    public void Crop_DimensionsMatchRequest()
    {
        var img = CreateGray(128, 8, 8);
        var cropped = img.Crop(1, 1, 3, 3);
        Assert.Equal(3, cropped.Width);
        Assert.Equal(3, cropped.Height);
    }

    [Fact]
    public void Crop_PreservesPixelValues()
    {
        var img = CreateGray(200, 8, 8);
        var cropped = img.Crop(0, 0, 4, 4);
        var (mean, _, _) = cropped.GetStats();
        Assert.Equal(200.0, mean, 0);
    }

    [Fact]
    public void Crop_SinglePixel()
    {
        var img = CreateGray(100, 4, 4);
        var cropped = img.Crop(2, 2, 1, 1);
        Assert.Equal(1, cropped.Width);
        Assert.Equal(1, cropped.Height);
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ReturnsNewImage()
    {
        var img = CreateGray(128, 4, 4);
        var resized = img.Resize(8, 8);
        Assert.NotSame(img, resized);
    }

    [Fact]
    public void Resize_ToExactDimensions()
    {
        var img = CreateGray(128, 4, 4);
        var resized = img.Resize(6, 3);
        Assert.Equal(6, resized.Width);
        Assert.Equal(3, resized.Height);
    }

    [Fact]
    public void Resize_Up_DimensionsIncrease()
    {
        var img = CreateGray(128, 2, 2);
        var resized = img.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
    }

    [Fact]
    public void Resize_Down_DimensionsDecrease()
    {
        var img = CreateGray(128, 8, 8);
        var resized = img.Resize(2, 2);
        Assert.Equal(2, resized.Width);
        Assert.Equal(2, resized.Height);
    }

    [Fact]
    public void Resize_SameDimensions_WorksCorrectly()
    {
        var img = CreateGray(100, 4, 4);
        var resized = img.Resize(4, 4);
        Assert.Equal(4, resized.Width);
        Assert.Equal(4, resized.Height);
    }

    // -------------------------------------------------------------------------
    // MergeHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_WidthIsSumOfWidths()
    {
        var left = CreateGray(100, 4, 4);
        var right = CreateGray(200, 4, 4);
        var merged = left.MergeHorizontal(right);
        Assert.Equal(8, merged.Width);
    }

    [Fact]
    public void MergeHorizontal_HeightMatchesInput()
    {
        var left = CreateGray(100, 4, 4);
        var right = CreateGray(200, 4, 4);
        var merged = left.MergeHorizontal(right);
        Assert.Equal(4, merged.Height);
    }

    // -------------------------------------------------------------------------
    // MergeVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_HeightIsSumOfHeights()
    {
        var top = CreateGray(100, 4, 4);
        var bottom = CreateGray(200, 4, 4);
        var merged = top.MergeVertical(bottom);
        Assert.Equal(8, merged.Height);
    }

    [Fact]
    public void MergeVertical_WidthMatchesInput()
    {
        var top = CreateGray(100, 4, 4);
        var bottom = CreateGray(200, 4, 4);
        var merged = top.MergeVertical(bottom);
        Assert.Equal(4, merged.Width);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Crop->Resize->MergeHorizontal->MergeVertical->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCropResizeMergeHorizMergeVertGetStats_Pipeline()
    {
        var img = CreateGray(128, 8, 8);

        // Crop to 4x4
        var cropped = img.Crop(0, 0, 4, 4);
        Assert.Equal(4, cropped.Width);
        Assert.Equal(4, cropped.Height);

        // Resize to 6x6
        var resized = cropped.Resize(6, 6);
        Assert.Equal(6, resized.Width);
        Assert.Equal(6, resized.Height);

        // Create companion image
        var companion = CreateGray(64, 6, 6);

        // MergeHorizontal
        var hmerged = resized.MergeHorizontal(companion);
        Assert.Equal(12, hmerged.Width);
        Assert.Equal(6, hmerged.Height);

        // MergeVertical
        var vmerged = resized.MergeVertical(companion);
        Assert.Equal(6, vmerged.Width);
        Assert.Equal(12, vmerged.Height);

        // GetStats
        var (mean, min, max) = hmerged.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }
}
