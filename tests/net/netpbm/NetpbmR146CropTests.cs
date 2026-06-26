// Tests for NetpbmImage.Crop dedicated coverage.
// Sprint: ff-sprint-s150-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R146

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R146: Dedicated tests for NetpbmImage.Crop(int top, int left, int cropHeight, int cropWidth).
/// Crop returns a new image with the specified region extracted.
/// Throws ArgumentOutOfRangeException if dimensions are invalid or region exceeds bounds.
/// Covers: negative top throws; negative left throws; zero height throws; zero width throws;
/// crop region exceeds image bounds throws; output dimensions match crop size;
/// output format preserved; top-left pixel correct; original unchanged after crop;
/// dogfood Create->SetPixel->Crop->GetPixel pipeline;
/// dogfood crop full image returns same dimensions.
/// </summary>
public class NetpbmR146CropTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NegativeTop_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Crop(-1, 0, 2, 2));
    }

    [Fact]
    public void Crop_NegativeLeft_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Crop(0, -1, 2, 2));
    }

    [Fact]
    public void Crop_ZeroHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Crop(0, 0, 0, 2));
    }

    [Fact]
    public void Crop_ZeroWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Crop(0, 0, 2, 0));
    }

    [Fact]
    public void Crop_RegionExceedsBounds_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5); // 4 wide, 4 tall
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Crop(0, 0, 5, 2)); // height 5 > image height 4
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_OutputDimensionsMatchCropSize()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var cropped = img.Crop(1, 2, 3, 4); // height=3, width=4
        Assert.Equal(4, cropped.Width);
        Assert.Equal(3, cropped.Height);
    }

    [Fact]
    public void Crop_PreservesFormat()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var cropped = img.Crop(0, 0, 2, 2);
        Assert.Equal(NetpbmFormat.PGM_P5, cropped.Format);
    }

    [Fact]
    public void Crop_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 99);
        _ = img.Crop(0, 0, 2, 2);
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
        Assert.Equal(99, img.GetPixel(0, 0));
    }

    [Fact]
    public void Crop_TopLeftPixel_CorrectValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 2, 77); // row=1, col=2
        var cropped = img.Crop(1, 2, 2, 2); // top=1, left=2, h=2, w=2
        Assert.Equal(77, cropped.GetPixel(0, 0)); // top-left of crop
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_Crop_GetPixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 2, 123); // center
        img.SetPixel(2, 3, 200); // one to the right

        var cropped = img.Crop(2, 2, 1, 2); // 1 row, 2 cols starting at (2,2)
        Assert.Equal(123, cropped.GetPixel(0, 0));
        Assert.Equal(200, cropped.GetPixel(0, 1));
    }

    [Fact]
    public void DogfoodPipeline_CropFullImage_ReturnsSameDimensions()
    {
        var img = NetpbmImage.Create(3, 5, NetpbmFormat.PGM_P5);
        var cropped = img.Crop(0, 0, 5, 3); // entire image
        Assert.Equal(img.Width, cropped.Width);
        Assert.Equal(img.Height, cropped.Height);
    }
}
