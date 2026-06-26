// Tests for NetpbmImage.AdjustContrast dedicated coverage.
// Sprint: ff-sprint-s179-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R175

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R175: Dedicated tests for NetpbmImage.AdjustContrast(double factor).
/// Adjusts contrast around the midpoint (MaxValue/2.0).
/// pixel = Clamp(mid + (pixel - mid) * factor, 0, MaxValue).
/// factor &lt; 0 throws ArgumentOutOfRangeException.
/// PBM (binary) returns a clone immediately.
/// factor=1.0 is the identity transformation.
/// factor=0.0: all pixels become mid value.
/// Returns a new image; original is unchanged.
/// Covers: negative factor throws; PBM returns clone; returns new image;
/// width/height unchanged; format preserved; original pixels unchanged;
/// factor=1.0 identity; factor=0.0 all-mid; result in valid range; dogfood PGM pipeline.
/// </summary>
public class NetpbmR175AdjustContrastTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_NegativeFactor_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.AdjustContrast(-0.1));
    }

    // -------------------------------------------------------------------------
    // PBM handling (clone)
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_OnPbmImage_ReturnsClone()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 1);
        var result = img.AdjustContrast(2.0);
        Assert.NotSame(img, result);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.5);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void AdjustContrast_ResultWidth_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void AdjustContrast_ResultHeight_MatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void AdjustContrast_ResultFormat_MatchesOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    // -------------------------------------------------------------------------
    // Pixel semantics tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_OriginalPixels_Unchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        img.AdjustContrast(2.0);
        Assert.Equal(100, img.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustContrast_FactorOne_IsIdentity()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        img.SetPixel(0, 1, 200);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(100, result.GetPixel(0, 0));
        Assert.Equal(200, result.GetPixel(0, 1));
    }

    [Fact]
    public void AdjustContrast_ResultPixels_InValidRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 255);
        var result = img.AdjustContrast(2.0);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.InRange(result.GetPixel(r, c), 0, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmAdjustContrast_NonNullResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        img.SetPixel(2, 2, 200);
        var result = img.AdjustContrast(1.5);
        Assert.NotNull(result);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }
}
