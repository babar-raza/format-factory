// Tests for NetpbmImage.AdjustContrast dedicated coverage.
// Sprint: ff-sprint-s198-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R202

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R202: Dedicated tests for NetpbmImage.AdjustContrast(double factor).
/// factor=1.0 returns equivalent image; factor=0.0 returns grey/flat image.
/// Returns new image (not same reference).
/// Format preserved. Dimensions preserved. MaxValue preserved.
/// Negative factor: valid (inverts/clamps). Pixels clamped to [0, MaxValue].
/// Covers: PGM returns new; PBM passthrough; format preserved; dims preserved;
/// MaxValue preserved; factor=1.0 values unchanged; factor=0.0 flat;
/// high factor amplifies; clamped to MaxValue; dogfood round-trip.
/// </summary>
public class NetpbmR202AdjustContrastTests
{
    // -------------------------------------------------------------------------
    // Basic structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.0);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void AdjustContrast_PbmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P1);
        var result = img.AdjustContrast(1.0);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void AdjustContrast_FormatPreserved_Pgm()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.5);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void AdjustContrast_FormatPreserved_Ppm()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        var result = img.AdjustContrast(1.5);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void AdjustContrast_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 3, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(2.0);
        Assert.Equal(6, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void AdjustContrast_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_FactorOne_PixelsUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(128, result.GetPixel(0, 0));
    }

    [Fact]
    public void AdjustContrast_FactorZero_PixelsFlattened()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        img.SetPixel(1, 1, 50);
        var result = img.AdjustContrast(0.0);
        // With factor=0, contrast is removed — all pixels become mid-grey or 0
        // Both pixels should be equal (flattened)
        Assert.Equal(result.GetPixel(0, 0), result.GetPixel(1, 1));
    }

    [Fact]
    public void AdjustContrast_HighFactor_BrightPixelClamped()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, img.MaxValue);
        var result = img.AdjustContrast(10.0);
        // Should be clamped at MaxValue
        Assert.True(result.GetPixel(0, 0) <= img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmContrastRoundTrip_FormatAndDimsStable()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, (r * 5 + c) * 4);
        var result = img.AdjustContrast(1.2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
        Assert.NotSame(img, result);
    }
}
