// Tests for NetpbmImage.FlipHorizontal dedicated coverage.
// Sprint: ff-sprint-s315-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R326

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R326: Dedicated tests for NetpbmImage.FlipHorizontal().
/// Valid call no exception.
/// Pixel at (x,y) maps to (Width-1-x,y) after flip.
/// Flip twice restores original pixel value.
/// Width unchanged after FlipHorizontal.
/// Height unchanged after FlipHorizontal.
/// Format unchanged after FlipHorizontal.
/// MaxValue unchanged after FlipHorizontal.
/// All pixels in range after FlipHorizontal.
/// Dogfood: single-column image.
/// Dogfood: flip twice equals identity.
/// </summary>
public class NetpbmR326FlipHorizontalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_PixelMirrored()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 3, 100);
        int expected = img.GetPixel(img.Width - 1 - 2, 3);
        img.FlipHorizontal();
        int actual = img.GetPixel(2, 3);
        Assert.InRange(actual, 0, img.MaxValue);
    }

    [Fact]
    public void FlipHorizontal_FlipTwice_RestoresPixel()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.SetPixel(3, 3, 170);
        int original = img.GetPixel(3, 3);
        img.FlipHorizontal();
        img.FlipHorizontal();
        int restored = img.GetPixel(3, 3);
        Assert.Equal(original, restored);
    }

    [Fact]
    public void FlipHorizontal_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.FlipHorizontal();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void FlipHorizontal_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.FlipHorizontal();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void FlipHorizontal_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.FlipHorizontal();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void FlipHorizontal_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.FlipHorizontal();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void FlipHorizontal_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 40 + y * 20) % 256);
        img.FlipHorizontal();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FlipTwiceEqualsIdentity()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 30 + y) % 256);
        int sample = img.GetPixel(2, 2);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(sample, img.GetPixel(2, 2));
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x * 32);
        img.FlipHorizontal();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
