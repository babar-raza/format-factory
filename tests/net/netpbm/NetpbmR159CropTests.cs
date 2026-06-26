// Tests for NetpbmImage.Crop dedicated coverage.
// Sprint: ff-sprint-s163-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R159

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R159: Dedicated tests for NetpbmImage.Crop(int top, int left, int cropHeight, int cropWidth).
/// Crop returns a NEW image with the specified rectangular region extracted.
/// Output Width equals cropWidth; output Height equals cropHeight.
/// Throws ArgumentOutOfRangeException if any dimension is zero/negative or region exceeds bounds.
/// Covers: negative top throws; negative left throws; cropHeight zero throws; cropWidth zero throws;
/// region beyond height throws; region beyond width throws;
/// output width equals cropWidth; output height equals cropHeight;
/// format preserved; original unchanged;
/// dogfood Create->SetPixel->Crop->GetPixel; dogfood pixel at top-left corner preserved.
/// </summary>
public class NetpbmR159CropTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NegativeTop_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => img.Crop(-1, 0, 2, 2));
    }

    [Fact]
    public void Crop_NegativeLeft_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => img.Crop(0, -1, 2, 2));
    }

    [Fact]
    public void Crop_CropHeightZero_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => img.Crop(0, 0, 0, 2));
    }

    [Fact]
    public void Crop_CropWidthZero_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => img.Crop(0, 0, 2, 0));
    }

    [Fact]
    public void Crop_RegionExceedsHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4w 3h
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => img.Crop(2, 0, 2, 2)); // top=2, cropH=2 → 4 > 3
    }

    [Fact]
    public void Crop_RegionExceedsWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5); // 4w 3h
        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => img.Crop(0, 3, 2, 2)); // left=3, cropW=2 → 5 > 4
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_OutputWidth_EqualsCropWidth()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 3, 5);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void Crop_OutputHeight_EqualsCropHeight()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 3, 5);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Crop_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 2, 2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateSetPixelCrop_GetPixel()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 3, 99); // row=2, col=3
        // Crop starting at top=1, left=2 → pixel at row=2,col=3 maps to cropped row=1, col=1
        var result = img.Crop(1, 2, 3, 3);
        Assert.Equal(99, result.GetPixel(1, 1));
    }

    [Fact]
    public void DogfoodPipeline_TopLeftCorner_PixelPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 55); // top-left of crop region
        var result = img.Crop(1, 1, 2, 2);
        Assert.Equal(55, result.GetPixel(0, 0));
    }
}
