// Tests for NetpbmImage.Equalize dedicated coverage.
// Sprint: ff-sprint-s176-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R172

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R172: Dedicated tests for NetpbmImage.Equalize().
/// Applies histogram equalization to enhance contrast.
/// PBM (already binary) returns a clone immediately.
/// PPM is converted to grayscale before equalization.
/// A uniform image (all pixels same value) is unaffected (denominator=0 → clone).
/// Returns a new image; original is unchanged.
/// Covers: PBM returns clone; returns new image; width/height unchanged;
/// format preserved; original unchanged; uniform image same value;
/// all-zero stays zero; result pixels in valid range; dogfood PGM pipeline.
/// </summary>
public class NetpbmR172EqualizeTests
{
    // -------------------------------------------------------------------------
    // PBM handling
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_OnPbmImage_ReturnsClone()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 1);
        var result = img.Equalize();
        Assert.NotSame(img, result);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 200);
        var result = img.Equalize();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Equalize_ResultWidth_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Equalize();
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void Equalize_ResultHeight_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Equalize();
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Equalize_ResultFormat_MatchesOriginalFormat()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Equalize();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    // -------------------------------------------------------------------------
    // Pixel semantics tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_OriginalPixels_Unchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        img.SetPixel(0, 1, 200);
        img.Equalize();
        Assert.Equal(100, img.GetPixel(0, 0));
        Assert.Equal(200, img.GetPixel(0, 1));
    }

    [Fact]
    public void Equalize_UniformImage_ReturnsCloneWithSameValues()
    {
        // All same pixel → CDF denominator=0 → returns clone
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        img.SetPixel(0, 1, 128);
        img.SetPixel(1, 0, 128);
        img.SetPixel(1, 1, 128);
        var result = img.Equalize();
        Assert.Equal(128, result.GetPixel(0, 0));
    }

    [Fact]
    public void Equalize_AllZeroImage_ResultPixelsAreZero()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        // all pixels default to 0
        var result = img.Equalize();
        Assert.Equal(0, result.GetPixel(0, 0));
    }

    [Fact]
    public void Equalize_ResultPixels_InValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 200);
        img.SetPixel(3, 3, 255);
        var result = img.Equalize();
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.InRange(result.GetPixel(r, c), 0, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmCreate_EqualizeThenInspect()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 85);
        img.SetPixel(1, 0, 170);
        img.SetPixel(1, 1, 255);
        var result = img.Equalize();
        Assert.NotNull(result);
        Assert.Equal(2, result.Width);
        Assert.Equal(2, result.Height);
    }
}
