// Tests for NetpbmImage.Posterize dedicated coverage.
// Sprint: ff-sprint-s210-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R216

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R216: Dedicated tests for NetpbmImage.Posterize(int levels).
/// levels less than 2 → ArgumentOutOfRangeException (or ArgumentException).
/// PGM: returns new image.
/// PPM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Dimensions preserved.
/// All output pixels in valid range.
/// Original unchanged after posterize.
/// Dogfood: posterize levels=2, all distinct pixel values.
/// Dogfood: posterize on uniform image.
/// </summary>
public class NetpbmR216PosterizeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_LevelsLessThanTwo_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Posterize(1));
    }

    [Fact]
    public void Posterize_ZeroLevels_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Posterize(0));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Posterize(4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Posterize_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.Posterize(4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Posterize_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Posterize(4);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Posterize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Posterize(4);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void Posterize_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var result = img.Posterize(3);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, (x * 50 + y * 10) % 256);
        var result = img.Posterize(4);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    [Fact]
    public void Posterize_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 123);
        var _ = img.Posterize(4);
        Assert.Equal(123, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_AllSameAfterPosterize()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 80);
        var result = img.Posterize(4);
        int first = result.GetPixel(0, 0);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.Equal(first, result.GetPixel(x, y));
    }

    [Fact]
    public void DogfoodPipeline_FormatDimsChained()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Posterize(8);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
        Assert.Equal(255, result.MaxValue);
    }
}
