// Tests for NetpbmImage.Emboss dedicated coverage.
// Sprint: ff-sprint-s200-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R204

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R204: Dedicated tests for NetpbmImage.Emboss().
/// Returns a new image (not same reference).
/// Format preserved. Dimensions preserved. MaxValue preserved.
/// PBM: returns clone (binary format passthrough).
/// PGM: applies emboss kernel; result is a new image.
/// PPM: format and dims preserved.
/// All output pixels clamped to [0, MaxValue].
/// Uniform image → emboss has no edges → flat/uniform output.
/// Dogfood: emboss PGM, format and dims stable.
/// Dogfood: emboss then check not same as original.
/// </summary>
public class NetpbmR204EmbossTests
{
    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Emboss_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Emboss();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Emboss_PbmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PBM_P1);
        var result = img.Emboss();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Emboss_PpmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.Emboss();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Emboss_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Emboss();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Emboss_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.Emboss();
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Emboss_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(8, 3, NetpbmFormat.PGM_P5);
        var result = img.Emboss();
        Assert.Equal(8, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Emboss_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Emboss();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Emboss_AllPixelsClamped()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, img.MaxValue);
        var result = img.Emboss();
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                Assert.True(result.GetPixel(r, c) >= 0 && result.GetPixel(r, c) <= img.MaxValue);
    }

    [Fact]
    public void Emboss_UniformImage_PixelsNonNegative()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, 100);
        var result = img.Emboss();
        // All embossed pixels should be within valid range
        Assert.True(result.GetPixel(2, 2) >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_EmbossPgm_FormatAndDimsStable()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                img.SetPixel(r, c, (r * 6 + c) * 4);
        var result = img.Emboss();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(6, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void DogfoodPipeline_EmbossTwice_NotSameAsOriginal()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        img.SetPixel(4, 4, 50);
        var r1 = img.Emboss();
        var r2 = r1.Emboss();
        Assert.NotSame(img, r1);
        Assert.NotSame(r1, r2);
    }
}
