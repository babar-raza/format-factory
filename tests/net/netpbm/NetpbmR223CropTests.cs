// Tests for NetpbmImage.Crop dedicated coverage.
// Sprint: ff-sprint-s217-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R223

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R223: Dedicated tests for NetpbmImage.Crop(int x, int y, int width, int height).
/// Out-of-bounds x → throws exception.
/// Out-of-bounds y → throws exception.
/// Zero width → throws exception.
/// Zero height → throws exception.
/// PGM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Result has specified dimensions.
/// All output pixels in valid range.
/// Dogfood: crop and verify centre pixel.
/// </summary>
public class NetpbmR223CropTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_XOutOfBounds_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(10, 0, 2, 2));
    }

    [Fact]
    public void Crop_YOutOfBounds_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(0, 10, 2, 2));
    }

    [Fact]
    public void Crop_ZeroWidth_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(0, 0, 0, 2));
    }

    [Fact]
    public void Crop_ZeroHeight_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(0, 0, 2, 0));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 4, 4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Crop_FormatPreserved()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 4, 4);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Crop_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Crop(0, 0, 4, 4);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void Crop_ResultHasSpecifiedWidth()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P5);
        var result = img.Crop(1, 1, 5, 3);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void Crop_ResultHasSpecifiedHeight()
    {
        var img = NetpbmImage.Create(10, 10, NetpbmFormat.PGM_P5);
        var result = img.Crop(1, 1, 5, 3);
        Assert.Equal(3, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                img.SetPixel(x, y, (x * 30 + y * 15) % 256);
        var result = img.Crop(2, 2, 4, 4);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CropPreservesCentrePixel()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 200);
        var result = img.Crop(1, 1, 4, 4);
        Assert.Equal(200, result.GetPixel(1, 1));
    }
}
