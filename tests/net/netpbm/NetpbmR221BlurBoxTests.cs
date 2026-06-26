// Tests for NetpbmImage.BlurBox dedicated coverage.
// Sprint: ff-sprint-s215-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R221

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R221: Dedicated tests for NetpbmImage.BlurBox(int radius).
/// Negative radius → throws exception.
/// PGM: returns new image.
/// PPM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Dimensions preserved.
/// All output pixels in valid range.
/// Original unchanged after blur.
/// Uniform image: all output pixels same after blur.
/// Dogfood: format/dims/MaxValue chain preserved.
/// </summary>
public class NetpbmR221BlurBoxTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_NegativeRadius_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.BlurBox(-1));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurBox_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.BlurBox(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurBox_FormatPreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void BlurBox_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.BlurBox(1);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void BlurBox_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 5, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.Equal(7, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, (x * 50 + y * 13) % 256);
        var result = img.BlurBox(1);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    [Fact]
    public void BlurBox_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 180);
        var _ = img.BlurBox(1);
        Assert.Equal(180, img.GetPixel(2, 2));
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
                img.SetPixel(x, y, 120);
        var result = img.BlurBox(1);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.Equal(120, result.GetPixel(x, y));
    }

    [Fact]
    public void DogfoodPipeline_FormatDimsMaxValueChained()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.BlurBox(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
        Assert.Equal(200, result.MaxValue);
    }
}
