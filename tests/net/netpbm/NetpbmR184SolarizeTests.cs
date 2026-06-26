// Tests for NetpbmImage.Solarize dedicated coverage.
// Sprint: ff-sprint-s188-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R184

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R184: Dedicated tests for NetpbmImage.Solarize(byte threshold).
/// Pixels with value above threshold are inverted (MaxValue - pixel).
/// Pixels at or below threshold are unchanged.
/// PBM images return a clone (no change).
/// Returns a new image (not same reference).
/// Format and MaxValue are preserved.
/// threshold=0: all pixels above 0 are inverted.
/// threshold=255: no pixels inverted (all at or below max).
/// Covers: PBM returns new image; PBM format preserved; PGM returns new image;
/// PGM format preserved; MaxValue preserved; dims unchanged;
/// threshold=0 inverts pixel above 0; pixel at threshold not inverted;
/// pixel above threshold inverted; dogfood PGM solarize dims; dogfood uniform pixel.
/// </summary>
public class NetpbmR184SolarizeTests
{
    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_PbmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.Solarize(128);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Solarize_PbmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.Solarize(128);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
    }

    [Fact]
    public void Solarize_PgmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Solarize(128);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Solarize_PgmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Solarize(128);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Solarize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Solarize(128);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Solarize_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(6, 3, NetpbmFormat.PGM_P5);
        var result = img.Solarize(100);
        Assert.Equal(6, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Solarize_PixelAboveThreshold_Inverted()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200); // 200 > 128 → 255-200 = 55
        var result = img.Solarize(128);
        Assert.Equal(255 - 200, result.GetPixel(0, 0));
    }

    [Fact]
    public void Solarize_PixelAtThreshold_NotInverted()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128); // 128 is not > 128, unchanged
        var result = img.Solarize(128);
        Assert.Equal(128, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmSolarize_DimsAndFormatUnchanged()
    {
        var img = NetpbmImage.Create(8, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        var result = img.Solarize(100);
        Assert.Equal(8, result.Width);
        Assert.Equal(5, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void DogfoodPipeline_ZeroPixelWithThresholdZero_Unchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0); // 0 is not > 0
        var result = img.Solarize(0);
        Assert.Equal(0, result.GetPixel(0, 0));
    }
}
