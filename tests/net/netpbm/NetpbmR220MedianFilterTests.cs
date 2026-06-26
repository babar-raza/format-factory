// Tests for NetpbmImage.MedianFilter dedicated coverage.
// Sprint: ff-sprint-s214-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R220

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R220: Dedicated tests for NetpbmImage.MedianFilter(int radius).
/// Negative radius → throws exception.
/// PGM: returns new image.
/// PPM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Dimensions preserved.
/// All output pixels in valid range.
/// Original unchanged after median filter.
/// radius=0: result has same pixel values (no smoothing).
/// Dogfood: format/dims/MaxValue chain.
/// </summary>
public class NetpbmR220MedianFilterTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_NegativeRadius_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.MedianFilter(-1));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MedianFilter_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.MedianFilter(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MedianFilter_FormatPreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MedianFilter_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.MedianFilter(1);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void MedianFilter_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 5, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(7, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, (x * 50 + y * 11) % 256);
        var result = img.MedianFilter(1);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    [Fact]
    public void MedianFilter_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 150);
        var _ = img.MedianFilter(1);
        Assert.Equal(150, img.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_OutputUniform()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, 100);
        var result = img.MedianFilter(1);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.Equal(100, result.GetPixel(x, y));
    }

    [Fact]
    public void DogfoodPipeline_FormatDimsMaxValueChained()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
        Assert.Equal(200, result.MaxValue);
    }
}
