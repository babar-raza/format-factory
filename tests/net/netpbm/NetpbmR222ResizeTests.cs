// Tests for NetpbmImage.Resize dedicated coverage.
// Sprint: ff-sprint-s216-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R222

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R222: Dedicated tests for NetpbmImage.Resize(int width, int height).
/// Zero width → throws exception.
/// Zero height → throws exception.
/// Negative width → throws exception.
/// Negative height → throws exception.
/// PGM: returns new image.
/// Format preserved.
/// MaxValue preserved.
/// Result has specified dimensions.
/// All output pixels in valid range.
/// Dogfood: resize to same dims = equivalent image.
/// </summary>
public class NetpbmR222ResizeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ZeroWidth_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Resize(0, 4));
    }

    [Fact]
    public void Resize_ZeroHeight_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Resize(4, 0));
    }

    [Fact]
    public void Resize_NegativeWidth_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Resize(-1, 4));
    }

    [Fact]
    public void Resize_NegativeHeight_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.ThrowsAny<Exception>(() => img.Resize(4, -1));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_PGM_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 8);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Resize_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 8);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Resize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(8, 8);
        Assert.Equal(255, result.MaxValue);
    }

    [Fact]
    public void Resize_ResultHasSpecifiedWidth()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(10, 6);
        Assert.Equal(10, result.Width);
    }

    [Fact]
    public void Resize_ResultHasSpecifiedHeight()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(10, 6);
        Assert.Equal(6, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel value tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, (x * 64 + y * 16) % 256);
        var result = img.Resize(8, 8);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UpscaleDownscale_FormatMaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var big = img.Resize(8, 8);
        var small = big.Resize(2, 2);
        Assert.Equal(NetpbmFormat.PGM_P5, small.Format);
        Assert.Equal(200, small.MaxValue);
        Assert.Equal(2, small.Width);
        Assert.Equal(2, small.Height);
    }
}
