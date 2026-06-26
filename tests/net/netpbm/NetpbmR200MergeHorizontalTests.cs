// Tests for NetpbmImage.MergeHorizontal dedicated coverage.
// Sprint: ff-sprint-s197-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R200

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R200: Dedicated tests for NetpbmImage.MergeHorizontal(NetpbmImage other).
/// null other → throws ArgumentNullException.
/// Height mismatch → throws ArgumentException.
/// Format mismatch → throws ArgumentException.
/// Valid merge: returns new image (not same reference).
/// Result height = base height (unchanged).
/// Result width = base.Width + other.Width.
/// Format is preserved.
/// MaxValue = max of both.
/// Left-half pixels come from base image.
/// Right-half pixels come from other image.
/// Covers: null throws; height mismatch throws; format mismatch throws;
/// returns new image; height same; width = sum; format preserved;
/// MaxValue max; left-half from base; dogfood PGM right-half pixel from other.
/// </summary>
public class NetpbmR200MergeHorizontalTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_NullOther_ThrowsArgumentNullException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentNullException>(() => img.MergeHorizontal(null!));
    }

    [Fact]
    public void MergeHorizontal_HeightMismatch_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(4, 5, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentException>(() => img.MergeHorizontal(other));
    }

    [Fact]
    public void MergeHorizontal_FormatMismatch_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(3, 4, NetpbmFormat.PBM_P1);
        Assert.Throws<ArgumentException>(() => img.MergeHorizontal(other));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_ValidMerge_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        var result = img.MergeHorizontal(other);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MergeHorizontal_ValidMerge_HeightSame()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        var result = img.MergeHorizontal(other);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void MergeHorizontal_ValidMerge_WidthIsSum()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        var result = img.MergeHorizontal(other);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void MergeHorizontal_ValidMerge_FormatPreserved()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        var result = img.MergeHorizontal(other);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MergeHorizontal_ValidMerge_MaxValueIsMax()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        var result = img.MergeHorizontal(other);
        Assert.Equal(Math.Max(img.MaxValue, other.MaxValue), result.MaxValue);
    }

    [Fact]
    public void MergeHorizontal_LeftHalf_PixelsFromBase()
    {
        var img = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 77); // top-left of base
        var other = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        var result = img.MergeHorizontal(other);
        Assert.Equal(77, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmRightHalf_PixelFromOther()
    {
        var left = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        // All left pixels = 50
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 3; c++)
                left.SetPixel(r, c, 50);
        var right = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        right.SetPixel(0, 0, 200); // first pixel of right becomes (row=0, col=3) in result
        var result = left.MergeHorizontal(right);
        // Column 3 of result should be pixel (0,0) of right
        Assert.Equal(200, result.GetPixel(0, 3));
        // Column 0 of result should still be from left
        Assert.Equal(50, result.GetPixel(0, 0));
    }
}
