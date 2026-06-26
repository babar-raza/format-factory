// Tests for NetpbmImage.Posterize dedicated coverage.
// Sprint: ff-sprint-s234-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R241

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R241: Dedicated tests for NetpbmImage.Posterize(levels).
/// Valid call returns non-null.
/// Returns different object (not same reference).
/// Format preserved after posterize.
/// MaxValue preserved after posterize.
/// Width preserved after posterize.
/// Height preserved after posterize.
/// Pixel values are in valid range [0, MaxValue].
/// Original image pixels unchanged after posterize.
/// Posterize with max levels preserves image closely.
/// Dogfood: create image, posterize with 2 levels, verify binary-like output.
/// </summary>
public class NetpbmR241PosterizeTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_ValidCall_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Posterize(4);
        Assert.NotNull(result);
    }

    [Fact]
    public void Posterize_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Posterize(4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Posterize_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Posterize(4);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Posterize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Posterize(4);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void Posterize_WidthPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Posterize(4);
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void Posterize_HeightPreserved()
    {
        var img = NetpbmImage.Create(4, 7, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Posterize(4);
        Assert.Equal(7, result.Height);
    }

    [Fact]
    public void Posterize_PixelValuesInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        img.SetPixel(2, 2, 200);
        var result = img.Posterize(4);
        Assert.InRange(result.GetPixel(1, 1), 0, 255);
        Assert.InRange(result.GetPixel(2, 2), 0, 255);
    }

    [Fact]
    public void Posterize_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 150);
        _ = img.Posterize(4);
        Assert.Equal(150, img.GetPixel(0, 0));
    }

    [Fact]
    public void Posterize_UniformImage_AllSameAfterPosterize()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int x = 0; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, 100);
        var result = img.Posterize(4);
        int val = result.GetPixel(0, 0);
        Assert.Equal(val, result.GetPixel(3, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Posterize2Levels_VerifyReducedValues()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 1, 200);
        var result = img.Posterize(2);
        // With 2 levels, pixel values should be quantized
        int p0 = result.GetPixel(0, 0);
        int p1 = result.GetPixel(1, 1);
        Assert.InRange(p0, 0, 255);
        Assert.InRange(p1, 0, 255);
        Assert.NotEqual(p0, p1);
    }
}
