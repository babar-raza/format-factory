// Tests for NetpbmImage.FlipHorizontal dedicated coverage.
// Sprint: ff-sprint-s268-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R276

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R276: Dedicated tests for NetpbmImage.FlipHorizontal().
/// Valid image no exception.
/// Pixel at (col, row) moves to (Width-1-col, row).
/// Flip twice restores original.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice no exception.
/// Dogfood: known pixel positions are swapped correctly.
/// Dogfood: flip twice original restored.
/// </summary>
public class NetpbmR276FlipHorizontalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard / functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_ValidImage_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_PixelMovesToMirroredColumn()
    {
        var img = NetpbmImage.CreateNew(4, 2, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 200); // col 0, row 0
        img.SetPixel(1, 0, 0);
        img.SetPixel(2, 0, 0);
        img.SetPixel(3, 0, 0);
        img.FlipHorizontal();
        // col 0 should now be at col 3
        Assert.Equal(200, img.GetPixel(3, 0));
    }

    [Fact]
    public void FlipHorizontal_FlipTwice_RestoresOriginal()
    {
        var img = NetpbmImage.CreateNew(4, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 150);
        img.SetPixel(3, 0, 75);
        int origLeft = img.GetPixel(0, 0);
        int origRight = img.GetPixel(3, 0);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(origLeft, img.GetPixel(0, 0));
        Assert.Equal(origRight, img.GetPixel(3, 0));
    }

    [Fact]
    public void FlipHorizontal_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.Pgm, 255);
        img.FlipHorizontal();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void FlipHorizontal_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.Pgm, 255);
        img.FlipHorizontal();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void FlipHorizontal_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        var fmt = img.Format;
        img.FlipHorizontal();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void FlipHorizontal_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 200);
        img.FlipHorizontal();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void FlipHorizontal_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => { img.FlipHorizontal(); img.FlipHorizontal(); });
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPositions_SwappedCorrectly()
    {
        // 6-wide image: pixel at col 0 = 10, col 5 = 250
        var img = NetpbmImage.CreateNew(6, 2, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(5, 0, 250);
        img.FlipHorizontal();
        Assert.Equal(10, img.GetPixel(5, 0));
        Assert.Equal(250, img.GetPixel(0, 0));
    }

    [Fact]
    public void DogfoodPipeline_FlipTwice_OriginalRestored()
    {
        var img = NetpbmImage.CreateNew(6, 2, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(5, 0, 250);
        img.SetPixel(2, 1, 130);
        int v0 = img.GetPixel(0, 0);
        int v5 = img.GetPixel(5, 0);
        int v2 = img.GetPixel(2, 1);
        img.FlipHorizontal();
        img.FlipHorizontal();
        Assert.Equal(v0, img.GetPixel(0, 0));
        Assert.Equal(v5, img.GetPixel(5, 0));
        Assert.Equal(v2, img.GetPixel(2, 1));
    }
}
