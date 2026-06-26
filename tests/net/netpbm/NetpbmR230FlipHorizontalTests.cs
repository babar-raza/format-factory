// Tests for NetpbmImage.FlipHorizontal dedicated coverage.
// Sprint: ff-sprint-s223-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R230

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R230: Dedicated tests for NetpbmImage.FlipHorizontal().
/// Returns new image (not same reference).
/// Format preserved.
/// MaxValue preserved.
/// Width preserved.
/// Height preserved.
/// All pixels in valid range.
/// Original image unchanged.
/// Flip-twice returns same pixel values as original.
/// Uniform image stays uniform after flip.
/// Dogfood: left pixel appears on right after flip.
/// </summary>
public class NetpbmR230FlipHorizontalTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipHorizontal();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void FlipHorizontal_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipHorizontal();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void FlipHorizontal_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.FlipHorizontal();
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void FlipHorizontal_WidthPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipHorizontal();
        Assert.Equal(6, result.Width);
    }

    [Fact]
    public void FlipHorizontal_HeightPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.FlipHorizontal();
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void FlipHorizontal_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 15);
        img.SetPixel(0, 0, 7);
        var result = img.FlipHorizontal();
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 15);
    }

    [Fact]
    public void FlipHorizontal_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        img.FlipHorizontal();
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void FlipHorizontal_FlipTwice_SamePixelValues()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 42);
        var result = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(42, result.GetPixel(0, 0));
    }

    [Fact]
    public void FlipHorizontal_UniformImage_StaysUniform()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 128);
        var result = img.FlipHorizontal();
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                Assert.Equal(128, result.GetPixel(x, y));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LeftPixelAppearsOnRight()
    {
        var img = NetpbmImage.Create(4, 1, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 99);  // left pixel = 99
        // After horizontal flip, pixel at x=0 should appear at x=width-1=3
        var result = img.FlipHorizontal();
        Assert.Equal(99, result.GetPixel(3, 0));
    }
}
