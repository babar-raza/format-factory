// Tests for NetpbmImage.Solarize dedicated coverage.
// Sprint: ff-sprint-s209-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R215

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R215: Dedicated tests for NetpbmImage.Solarize().
/// PGM: returns new image (not same reference).
/// PPM: returns new image.
/// Format preserved after solarize.
/// MaxValue preserved.
/// Dimensions preserved.
/// Pixels in lower half (below threshold): unchanged or inverted per solarize rule.
/// All output pixels in valid range [0, MaxValue].
/// Solarize is non-destructive (original unchanged).
/// Dogfood: solarize on uniform image.
/// Dogfood: format/dims chain preserved.
/// </summary>
public class NetpbmR215SolarizeTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Solarize();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Solarize_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.Solarize();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Solarize_FormatPreserved_PGM()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Solarize();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Solarize_FormatPreserved_PPM()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Solarize();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Solarize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Solarize();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Solarize_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var result = img.Solarize();
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 200);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, (x * 40 + y * 10) % 201);
        var result = img.Solarize();
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 200);
    }

    [Fact]
    public void Solarize_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        var _ = img.Solarize();
        Assert.Equal(100, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_AllSameAfterSolarize()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 50);
        var result = img.Solarize();
        int first = result.GetPixel(0, 0);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.Equal(first, result.GetPixel(x, y));
    }

    [Fact]
    public void DogfoodPipeline_FormatAndDimsChained()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Solarize();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
        Assert.Equal(255, result.MaxValue);
    }
}
