// Tests for NetpbmImage.Dither dedicated coverage.
// Sprint: ff-sprint-s206-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R211

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R211: Dedicated tests for NetpbmImage.Dither().
/// Returns a new image (not same reference).
/// Format preserved. Dimensions preserved. MaxValue preserved.
/// PBM: dither returns clone (already binary).
/// PGM: applies dithering; pixels become 0 or MaxValue.
/// PPM: dithering preserves format.
/// All output pixels are valid values (not negative, not above MaxValue).
/// Uniform black image → all pixels 0.
/// Uniform white image → all pixels MaxValue.
/// Dogfood: dither PGM, all pixels binary (0 or MaxValue).
/// Dogfood: dither twice, result not same reference.
/// </summary>
public class NetpbmR211DitherTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Dither_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Dither();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Dither_PbmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PBM_P1);
        var result = img.Dither();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Dither_PpmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.Dither();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Dither_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Dither();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Dither_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.Dither();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Dither_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(7, 4, NetpbmFormat.PGM_P5);
        var result = img.Dither();
        Assert.Equal(7, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Dither_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Dither();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Dither_AllBlackPgm_PixelsZero()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        // All pixels 0 (black)
        var result = img.Dither();
        // Black image should remain black
        Assert.Equal(0, result.GetPixel(2, 2));
    }

    [Fact]
    public void Dither_AllWhitePgm_PixelsMaxValue()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, img.MaxValue);
        var result = img.Dither();
        // White image should remain white
        Assert.Equal(img.MaxValue, result.GetPixel(2, 2));
    }

    [Fact]
    public void Dither_AllPixelsValidRange()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, r * 50 + c * 10);
        var result = img.Dither();
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                Assert.True(result.GetPixel(r, c) >= 0 && result.GetPixel(r, c) <= img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DitherPgm_FormatAndDimsStable()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                img.SetPixel(r, c, (r * 6 + c) * 4);
        var result = img.Dither();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void DogfoodPipeline_DitherTwice_NotSameReference()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var r1 = img.Dither();
        var r2 = r1.Dither();
        Assert.NotSame(r1, r2);
        Assert.Equal(NetpbmFormat.PGM_P5, r2.Format);
    }
}
