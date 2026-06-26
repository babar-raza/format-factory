// Tests for NetpbmImage.MergeVertical dedicated coverage.
// Sprint: ff-sprint-s196-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R199

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R199: Dedicated tests for NetpbmImage.MergeVertical(NetpbmImage other).
/// null other → throws ArgumentNullException.
/// Width mismatch → throws ArgumentException.
/// Format mismatch → throws ArgumentException.
/// Valid merge: returns new image (not same reference).
/// Result width = base width (unchanged).
/// Result height = base.Height + other.Height.
/// Format is preserved.
/// MaxValue = max of both.
/// Pixels from base are in top half of result.
/// Pixels from other are in bottom half of result.
/// Covers: null throws; width mismatch throws; format mismatch throws;
/// returns new image; result width same; result height = sum; format preserved;
/// MaxValue max; base pixels in top half; dogfood PGM stacked correct pixel.
/// </summary>
public class NetpbmR199MergeVerticalTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_NullOther_ThrowsArgumentNullException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentNullException>(() => img.MergeVertical(null!));
    }

    [Fact]
    public void MergeVertical_WidthMismatch_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentException>(() => img.MergeVertical(other));
    }

    [Fact]
    public void MergeVertical_FormatMismatch_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(4, 3, NetpbmFormat.PBM_P1);
        Assert.Throws<ArgumentException>(() => img.MergeVertical(other));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_ValidMerge_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        var result = img.MergeVertical(other);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MergeVertical_ValidMerge_WidthSame()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(5, 2, NetpbmFormat.PGM_P5);
        var result = img.MergeVertical(other);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void MergeVertical_ValidMerge_HeightIsSum()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        var result = img.MergeVertical(other);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void MergeVertical_ValidMerge_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        var result = img.MergeVertical(other);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MergeVertical_ValidMerge_MaxValueIsMax()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        var result = img.MergeVertical(other);
        Assert.Equal(Math.Max(img.MaxValue, other.MaxValue), result.MaxValue);
    }

    [Fact]
    public void MergeVertical_TopHalf_PixelsFromBase()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 111); // top row
        var other = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        var result = img.MergeVertical(other);
        Assert.Equal(111, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmStacked_BottomRowPixelFromOther()
    {
        var top = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        top.SetPixel(0, 0, 50);
        var bottom = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        bottom.SetPixel(0, 0, 200); // first row of 'bottom' becomes row 2 of result
        var result = top.MergeVertical(bottom);
        // Row 2 (index 2 in result) corresponds to row 0 of 'bottom'
        Assert.Equal(200, result.GetPixel(0, 2));
    }
}
