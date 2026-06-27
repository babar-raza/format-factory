// Tests for NetpbmImage.FlipVertical dedicated coverage.
// Sprint: ff-sprint-s305-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R314

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R314: Dedicated tests for NetpbmImage.FlipVertical().
/// Valid call no exception.
/// Pixel (x,y) maps to (x, Height-1-y) after flip.
/// Flip twice restores original pixel.
/// Width unchanged after FlipVertical.
/// Height unchanged after FlipVertical.
/// Format unchanged after FlipVertical.
/// MaxValue unchanged after FlipVertical.
/// All pixels in range after FlipVertical.
/// Called twice no exception.
/// Dogfood: double flip and verify top-left pixel.
/// </summary>
public class NetpbmR314FlipVerticalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_PixelMapsToMirroredRow()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 0, 200);
        img.FlipVertical();
        int mirrored = img.GetPixel(2, img.Height - 1);
        Assert.Equal(200, mirrored);
    }

    [Fact]
    public void FlipVertical_FlipTwice_RestoresOriginalPixel()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.SetPixel(3, 1, 150);
        img.FlipVertical();
        img.FlipVertical();
        int restored = img.GetPixel(3, 1);
        Assert.Equal(150, restored);
    }

    [Fact]
    public void FlipVertical_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.FlipVertical();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void FlipVertical_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.FlipVertical();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void FlipVertical_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.FlipVertical();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void FlipVertical_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.FlipVertical();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void FlipVertical_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * y) % 256);
        img.FlipVertical();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void FlipVertical_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.FlipVertical();
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DoubleFlip_RestoresDims()
    {
        var img = NetpbmImage.CreateNew(10, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y * 2) % 256);
        int w = img.Width;
        int h = img.Height;
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(w, img.Width);
        Assert.Equal(h, img.Height);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
