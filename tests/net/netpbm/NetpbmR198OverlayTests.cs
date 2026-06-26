// Tests for NetpbmImage.Overlay dedicated coverage.
// Sprint: ff-sprint-s195-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R198

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R198: Dedicated tests for NetpbmImage.Overlay(NetpbmImage overlay, int topOffset, int leftOffset).
/// Format mismatch → throws InvalidOperationException.
/// Negative topOffset → throws ArgumentOutOfRangeException.
/// Negative leftOffset → throws ArgumentOutOfRangeException.
/// Non-overlapping offsets (offset beyond base bounds) → returns clone unchanged.
/// Valid overlay: returns new image (not same reference).
/// Result format preserved.
/// Result dimensions equal base image dimensions.
/// MaxValue preserved.
/// Pixel in overlap region is from overlay.
/// Pixel outside overlap region is from base.
/// Covers: format mismatch throws; negative topOffset throws; negative leftOffset throws;
/// non-overlapping returns clone; returns new image; format preserved; dims unchanged;
/// MaxValue preserved; overlap pixel from overlay; dogfood PGM full overlay pixel value.
/// </summary>
public class NetpbmR198OverlayTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_FormatMismatch_ThrowsInvalidOperationException()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P1);
        Assert.Throws<InvalidOperationException>(() => base_.Overlay(over, 0, 0));
    }

    [Fact]
    public void Overlay_NegativeTopOffset_ThrowsArgumentOutOfRangeException()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => base_.Overlay(over, -1, 0));
    }

    [Fact]
    public void Overlay_NegativeLeftOffset_ThrowsArgumentOutOfRangeException()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => base_.Overlay(over, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Overlay_NonOverlapping_ReturnsNewImage()
    {
        // Overlay offset beyond base dims → no overlap → returns clone
        var base_ = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = base_.Overlay(over, 10, 10); // way out of bounds
        Assert.NotSame(base_, result);
    }

    [Fact]
    public void Overlay_ValidOverlay_ReturnsNewImage()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = base_.Overlay(over, 0, 0);
        Assert.NotSame(base_, result);
    }

    [Fact]
    public void Overlay_ValidOverlay_FormatPreserved()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Overlay_ValidOverlay_DimensionsUnchanged()
    {
        var base_ = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Overlay_ValidOverlay_MaxValuePreserved()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(base_.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Overlay_OverlapRegion_PixelFromOverlay()
    {
        var base_ = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        base_.SetPixel(0, 0, 50); // base pixel
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        over.SetPixel(0, 0, 200); // overlay pixel
        var result = base_.Overlay(over, 0, 0);
        Assert.Equal(200, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmFullOverlay_PixelReplaced()
    {
        var base_ = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                base_.SetPixel(r, c, 30);
        var over = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        over.SetPixel(0, 0, 180);
        var result = base_.Overlay(over, 1, 1);
        // Pixel at (1,1) should now be 180 (from overlay at (0,0))
        Assert.Equal(180, result.GetPixel(1, 1));
        // Pixel at (0,0) should still be 30 (from base)
        Assert.Equal(30, result.GetPixel(0, 0));
    }
}
