// Tests for NetpbmImage.Resize dedicated coverage.
// Sprint: ff-sprint-s242-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R249

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R249: Dedicated tests for NetpbmImage.Resize(int width, int height).
/// Returns new image (different object).
/// Result has specified width.
/// Result has specified height.
/// Format preserved.
/// MaxValue preserved.
/// Zero width → throws exception.
/// Zero height → throws exception.
/// Negative width → throws exception.
/// Upscale: result dimensions match requested.
/// Dogfood: resize then verify all pixels in valid range.
/// Dogfood: original unchanged after resize.
/// </summary>
public class NetpbmR249ResizeDedicatedTests
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

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ReturnsNewObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 8);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Resize_ResultHasSpecifiedWidth()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 6);
        Assert.Equal(8, result.Width);
    }

    [Fact]
    public void Resize_ResultHasSpecifiedHeight()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 6);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Resize_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(2, 2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Resize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Resize(8, 8);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void Resize_Upscale_DimensionsMatch()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(10, 10);
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PixelsInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(3, 3, 200);
        var result = img.Resize(8, 8);
        for (int row = 0; row < result.Height; row++)
            for (int col = 0; col < result.Width; col++)
                Assert.InRange(result.GetPixel(col, row), 0, result.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_OriginalUnchangedAfterResize()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 77);
        img.Resize(8, 8);
        // Original dimensions unchanged
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
        Assert.Equal(77, img.GetPixel(0, 0));
    }
}
