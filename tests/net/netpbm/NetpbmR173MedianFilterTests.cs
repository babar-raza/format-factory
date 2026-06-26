// Tests for NetpbmImage.MedianFilter dedicated coverage.
// Sprint: ff-sprint-s177-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R173

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R173: Dedicated tests for NetpbmImage.MedianFilter(int radius).
/// Applies median filter (noise reduction) using a square kernel of size (2*radius+1)^2.
/// radius &lt; 0 throws ArgumentOutOfRangeException.
/// radius == 0 returns a clone (identity).
/// Returns a new image; original is unchanged.
/// Uses clamped border extension (border pixels clamp to edge).
/// Covers: negative radius throws; radius=0 returns clone; returns new image;
/// width/height unchanged; format preserved; original pixels unchanged;
/// uniform image stays same; result pixels in valid range; dogfood PGM pipeline.
/// </summary>
public class NetpbmR173MedianFilterTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_NegativeRadius_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.MedianFilter(-1));
    }

    // -------------------------------------------------------------------------
    // Identity case
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_RadiusZero_ReturnsClone()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        var result = img.MedianFilter(0);
        Assert.NotSame(img, result);
        Assert.Equal(100, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MedianFilter_ResultWidth_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void MedianFilter_ResultHeight_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void MedianFilter_ResultFormat_MatchesOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    // -------------------------------------------------------------------------
    // Pixel semantics tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_OriginalPixels_Unchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 200);
        img.MedianFilter(1);
        Assert.Equal(200, img.GetPixel(1, 1));
    }

    [Fact]
    public void MedianFilter_UniformImage_PixelsUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(r, c, 128);
        var result = img.MedianFilter(1);
        Assert.Equal(128, result.GetPixel(1, 1));
    }

    [Fact]
    public void MedianFilter_ResultPixels_InValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 255);
        img.SetPixel(2, 2, 100);
        var result = img.MedianFilter(1);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.InRange(result.GetPixel(r, c), 0, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmCreate_MedianFilterPreservesShape()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 2, 255); // single spike
        var result = img.MedianFilter(1);
        Assert.NotNull(result);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }
}
