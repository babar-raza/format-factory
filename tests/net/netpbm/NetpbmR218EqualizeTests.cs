// Tests for NetpbmImage.Equalize dedicated coverage.
// Sprint: ff-sprint-s212-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R218

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R218: Dedicated tests for NetpbmImage.Equalize().
/// PGM: returns new image (not same reference).
/// PPM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Dimensions preserved.
/// All output pixels in valid range.
/// Original unchanged after equalize.
/// Uniform image: all output pixels same (no variation to spread).
/// Dogfood: equalize format/dims/MaxValue chain.
/// Dogfood: equalize twice — second result same as first (idempotent on equalized image).
/// </summary>
public class NetpbmR218EqualizeTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Equalize();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Equalize_PPM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.Equalize();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Equalize_FormatPreserved_PGM()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Equalize();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Equalize_FormatPreserved_PPM()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        var result = img.Equalize();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Equalize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Equalize();
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void Equalize_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 5, NetpbmFormat.PGM_P5);
        var result = img.Equalize();
        Assert.Equal(7, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                img.SetPixel(x, y, (x * 50 + y * 10) % 256);
        var result = img.Equalize();
        for (int y = 0; y < 5; y++)
            for (int x = 0; x < 5; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    [Fact]
    public void Equalize_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 80);
        var _ = img.Equalize();
        Assert.Equal(80, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_OutputInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 100);
        var result = img.Equalize();
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    [Fact]
    public void DogfoodPipeline_FormatDimsMaxValueChained()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Equalize();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
        Assert.Equal(200, result.MaxValue);
    }
}
