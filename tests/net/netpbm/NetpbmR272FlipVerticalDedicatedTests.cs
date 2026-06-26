// Tests for NetpbmImage.FlipVertical dedicated coverage.
// Sprint: ff-sprint-s265-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R272

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R272: Dedicated tests for NetpbmImage.FlipVertical().
/// FlipVertical flips the image upside-down in-place (void).
/// Width unchanged. Height unchanged.
/// Format unchanged. MaxValue unchanged.
/// Pixel at (col, row) moves to (col, Height-1-row).
/// Flip twice restores original pixel values.
/// All-zero image stays all-zero after flip.
/// Dogfood: set known pixels, flip, verify positions swapped.
/// Dogfood: flip twice, verify pixel restoration.
/// </summary>
public class NetpbmR272FlipVerticalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_ValidImage_NoException()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_PixelMirrorsVertically()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 99); // top-left becomes bottom-left
        img.FlipVertical();
        // After flip, pixel at row 0 should be at row 3 (H-1-0)
        Assert.Equal(99, img.GetPixel(0, 3));
    }

    [Fact]
    public void FlipVertical_FlipTwice_RestoresPixel()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 0, 77);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(77, img.GetPixel(1, 0));
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void FlipVertical_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void FlipVertical_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.FlipVertical();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void FlipVertical_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 150);
        img.FlipVertical();
        Assert.Equal(150, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixels_PositionsSwapped()
    {
        var img = NetpbmImage.Create(2, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10); // top
        img.SetPixel(0, 2, 90); // bottom
        img.FlipVertical();
        // After flip: top (row 0) should have what was at row 2 (bottom)
        Assert.Equal(90, img.GetPixel(0, 0));
        // And bottom (row 2) should have what was at row 0 (top)
        Assert.Equal(10, img.GetPixel(0, 2));
    }

    [Fact]
    public void DogfoodPipeline_FlipTwice_OriginalRestored()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 55);
        img.SetPixel(2, 2, 200);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(55, img.GetPixel(0, 0));
        Assert.Equal(200, img.GetPixel(2, 2));
    }
}
