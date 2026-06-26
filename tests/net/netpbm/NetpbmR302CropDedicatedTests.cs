// Tests for NetpbmImage.Crop dedicated coverage.
// Sprint: ff-sprint-s294-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R302

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R302: Dedicated tests for NetpbmImage.Crop(x, y, width, height).
/// Valid call no exception.
/// Cropped image has expected width.
/// Cropped image has expected height.
/// Format unchanged after Crop.
/// MaxValue unchanged after Crop.
/// All pixels in [0, MaxValue] after Crop.
/// Crop covers full image no exception.
/// Crop single pixel no exception.
/// Dogfood: crop and verify pixel from known position.
/// Dogfood: crop sub-region preserves pixel value.
/// </summary>
public class NetpbmR302CropDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 128);
        var ex = Record.Exception(() => img.Crop(1, 1, 4, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void Crop_ResultHasExpectedWidth()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM, 255);
        img.Crop(1, 1, 4, 3);
        Assert.Equal(4, img.Width);
    }

    [Fact]
    public void Crop_ResultHasExpectedHeight()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM, 255);
        img.Crop(1, 1, 4, 3);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Crop_FormatUnchanged()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.Crop(0, 0, 4, 3);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void Crop_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.Crop(0, 0, 4, 3);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void Crop_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 100);
        img.SetPixel(5, 4, 200);
        img.Crop(1, 1, 5, 4);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Crop_FullImage_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int w = img.Width;
        int h = img.Height;
        var ex = Record.Exception(() => img.Crop(0, 0, w, h));
        Assert.Null(ex);
    }

    [Fact]
    public void Crop_SinglePixel_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 77);
        var ex = Record.Exception(() => img.Crop(2, 2, 1, 1));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CropSinglePixel_VerifyPixelValue()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM, 255);
        img.SetPixel(3, 3, 200);
        img.Crop(3, 3, 1, 1);
        Assert.Equal(200, img.GetPixel(0, 0));
    }

    [Fact]
    public void DogfoodPipeline_CropSubRegion_PreservesPixelValue()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM, 255);
        img.SetPixel(4, 4, 150);
        img.Crop(3, 3, 3, 3);
        // pixel (4,4) in original → (1,1) in cropped region
        Assert.Equal(150, img.GetPixel(1, 1));
    }
}
