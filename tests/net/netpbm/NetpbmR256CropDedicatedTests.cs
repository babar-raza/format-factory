// Tests for NetpbmImage.Crop dedicated coverage.
// Sprint: ff-sprint-s249-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R256

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R256: Dedicated tests for NetpbmImage.Crop(x, y, width, height).
/// Crop extracts a rectangular region and returns a NEW image (non-destructive).
/// The original image is unchanged. Result dimensions match the requested w/h.
/// Result format and MaxValue match the original.
/// Covers: negative x throws; negative y throws; zero width throws; zero height throws;
/// OOB crop throws; result is non-null; result dimensions match requested;
/// format and MaxValue preserved in result; original unchanged after crop;
/// dogfood pixel values in cropped region match original.
/// </summary>
public class NetpbmR256CropDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NegativeX_ThrowsException()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(-1, 0, 4, 3));
    }

    [Fact]
    public void Crop_NegativeY_ThrowsException()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(0, -1, 4, 3));
    }

    [Fact]
    public void Crop_ZeroWidth_ThrowsException()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(0, 0, 0, 3));
    }

    [Fact]
    public void Crop_ZeroHeight_ThrowsException()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Crop(0, 0, 4, 0));
    }

    [Fact]
    public void Crop_OutOfBounds_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        // Crop region exceeds image bounds
        Assert.ThrowsAny<Exception>(() => img.Crop(2, 2, 4, 4));
    }

    // -------------------------------------------------------------------------
    // Result correctness tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_ValidRegion_ResultNotNull()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 4, 3);
        Assert.NotNull(result);
    }

    [Fact]
    public void Crop_ResultWidth_MatchesRequested()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 3, 2);
        Assert.Equal(3, result.Width);
    }

    [Fact]
    public void Crop_ResultHeight_MatchesRequested()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Crop(0, 0, 3, 2);
        Assert.Equal(2, result.Height);
    }

    [Fact]
    public void Crop_ResultFormat_MatchesOriginal()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Crop(1, 1, 3, 2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Crop_ResultMaxValue_MatchesOriginal()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Crop(0, 0, 4, 3);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void Crop_OriginalDimensions_UnchangedAfterCrop()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        img.Crop(0, 0, 4, 3);
        Assert.Equal(8, img.Width);
        Assert.Equal(6, img.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CroppedPixelsMatchOriginal()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        // Set some pixels in a region we'll crop
        img.SetPixel(1, 1, 77);
        img.SetPixel(2, 1, 88);
        img.SetPixel(1, 2, 99);
        // Crop from (1,1) with size 2x2
        var result = img.Crop(1, 1, 2, 2);
        Assert.Equal(2, result.Width);
        Assert.Equal(2, result.Height);
        // Pixel at result(0,0) should match original(1,1)
        Assert.Equal(77, result.GetPixel(0, 0));
    }
}
