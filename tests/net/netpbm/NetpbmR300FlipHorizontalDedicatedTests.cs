// Tests for NetpbmImage.FlipHorizontal dedicated coverage.
// Sprint: ff-sprint-s292-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R300

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R300: Dedicated tests for NetpbmImage.FlipHorizontal().
/// Valid call no exception.
/// Pixel (x,y) moves to (Width-1-x,y) after flip.
/// Flip twice restores original.
/// Width unchanged after FlipHorizontal.
/// Height unchanged after FlipHorizontal.
/// Format unchanged after FlipHorizontal.
/// MaxValue unchanged after FlipHorizontal.
/// All pixels in [0, MaxValue] after flip.
/// Called twice no exception.
/// Dogfood: known pixel survives double flip.
/// </summary>
public class NetpbmR300FlipHorizontalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_PixelMirrorsHorizontally()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 2, 100);
        int before = img.GetPixel(0, 2);
        img.FlipHorizontal();
        // pixel at (0,2) should now be at (Width-1-0,2) = (3,2)
        Assert.Equal(before, img.GetPixel(img.Width - 1, 2));
    }

    [Fact]
    public void FlipHorizontal_FlipTwice_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 77);
        img.SetPixel(3, 2, 200);
        int v1 = img.GetPixel(1, 1);
        int v2 = img.GetPixel(3, 2);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(v1, img.GetPixel(1, 1));
        Assert.Equal(v2, img.GetPixel(3, 2));
    }

    [Fact]
    public void FlipHorizontal_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.FlipHorizontal();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void FlipHorizontal_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.FlipHorizontal();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void FlipHorizontal_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.FlipHorizontal();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void FlipHorizontal_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.FlipHorizontal();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void FlipHorizontal_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(3, 3, 200);
        img.FlipHorizontal();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void FlipHorizontal_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 128);
        img.FlipHorizontal();
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixelSurvivesDoubleFlip()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 2, 150);
        img.SetPixel(4, 1, 210);
        int v1 = img.GetPixel(1, 2);
        int v2 = img.GetPixel(4, 1);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(v1, img.GetPixel(1, 2));
        Assert.Equal(v2, img.GetPixel(4, 1));
    }
}
