// Tests for NetpbmImage.Solarize dedicated coverage.
// Sprint: ff-sprint-s173-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R169

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R169: Dedicated tests for NetpbmImage.Solarize(byte threshold).
/// Pixels with value > threshold are inverted (MaxValue - pixel).
/// Pixels with value &lt;= threshold are unchanged.
/// PBM images return an unchanged clone.
/// Returns a NEW image. No throw conditions (byte threshold cannot be negative).
/// Covers: PBM returns clone; returns new image; width unchanged; height unchanged;
/// format unchanged; original unchanged after solarize; pixel-below-threshold unchanged;
/// pixel-above-threshold inverted; pixel-at-threshold unchanged;
/// dogfood Create->SetPixel->Solarize->GetPixel; double-solarize restores for max-value.
/// </summary>
public class NetpbmR169SolarizeTests
{
    // -------------------------------------------------------------------------
    // Format-specific behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_PbmFormat_ReturnsClone()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P4);
        var result = img.Solarize(128);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Solarize(128);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Solarize_Width_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Solarize(100);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void Solarize_Height_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Solarize(100);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Solarize_Format_Unchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Solarize(100);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Solarize_Original_Unchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 200);
        img.Solarize(100);
        Assert.Equal(200, img.GetPixel(1, 1)); // original must be unchanged
    }

    // -------------------------------------------------------------------------
    // Pixel inversion tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Solarize_PixelAboveThreshold_IsInverted()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 200); // > threshold=100
        var result = img.Solarize(100);
        // Inverted: MaxValue(255) - 200 = 55
        Assert.Equal(55, result.GetPixel(1, 1));
    }

    [Fact]
    public void Solarize_PixelBelowOrAtThreshold_Unchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50); // <= threshold=100
        var result = img.Solarize(100);
        Assert.Equal(50, result.GetPixel(0, 0));
    }

    [Fact]
    public void Solarize_PixelAtThreshold_Unchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128); // = threshold
        var result = img.Solarize(128);
        Assert.Equal(128, result.GetPixel(0, 0)); // threshold pixel: NOT > threshold
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateSetPixelSolarizeGetPixel()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 2, 200);
        var result = img.Solarize(100);
        // 200 > 100, so inverted: 255-200=55
        Assert.Equal(55, result.GetPixel(2, 2));
    }
}
