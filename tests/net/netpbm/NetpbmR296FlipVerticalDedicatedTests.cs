// Tests for NetpbmImage.FlipVertical dedicated coverage.
// Sprint: ff-sprint-s288-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R296

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R296: Dedicated tests for NetpbmImage.FlipVertical().
/// Valid call no exception.
/// All pixels in [0, MaxValue] after FlipVertical.
/// Pixel at (x, row) moves to (x, H-1-row) after flip.
/// Flip twice restores original pixel.
/// Width unchanged after FlipVertical.
/// Height unchanged after FlipVertical.
/// Format unchanged after FlipVertical.
/// MaxValue unchanged after FlipVertical.
/// Dogfood: set top row pixel, flip, check position.
/// Dogfood: uniform image flip no exception.
/// </summary>
public class NetpbmR296FlipVerticalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(2, 2, 200);
        img.FlipVertical();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void FlipVertical_PixelMovesToFlippedRow()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 200); // top-left
        img.FlipVertical();
        // pixel should now be at bottom-left (row = H-1 = 3)
        Assert.Equal(200, img.GetPixel(0, img.Height - 1));
    }

    [Fact]
    public void FlipVertical_FlipTwice_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 0, 150);
        int original = img.GetPixel(1, 0);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(original, img.GetPixel(1, 0));
    }

    [Fact]
    public void FlipVertical_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.FlipVertical();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void FlipVertical_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.FlipVertical();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void FlipVertical_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.FlipVertical();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void FlipVertical_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.FlipVertical();
        Assert.Equal(before, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetTopRowPixel_FlipMovesToBottom()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 0, 180); // row 0
        img.FlipVertical();
        Assert.Equal(180, img.GetPixel(2, img.Height - 1));
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_FlipNoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }
}
