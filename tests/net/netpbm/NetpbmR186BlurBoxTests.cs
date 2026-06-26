// Tests for NetpbmImage.BlurBox dedicated coverage.
// Sprint: ff-sprint-s190-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R186

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R186: Dedicated tests for NetpbmImage.BlurBox(int radius).
/// Applies a box blur filter averaging pixel values within the given radius window.
/// radius &lt; 1 throws ArgumentOutOfRangeException.
/// PBM images return a clone (no change).
/// Returns a new image (not same reference).
/// Format and MaxValue are preserved.
/// Dimensions unchanged.
/// radius=1 performs 3x3 box blur; larger radius is wider window.
/// Covers: radius=0 throws; radius negative throws; PBM returns new image;
/// PBM format preserved; PGM returns new image; PGM format preserved;
/// MaxValue preserved; dims unchanged; uniform image stays uniform;
/// dogfood PGM blur dims unchanged; dogfood radius=1 result is new image.
/// </summary>
public class NetpbmR186BlurBoxTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_ZeroRadius_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.BlurBox(0));
    }

    [Fact]
    public void BlurBox_NegativeRadius_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.BlurBox(-1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_PbmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.BlurBox(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurBox_PbmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.BlurBox(1);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
    }

    [Fact]
    public void BlurBox_PgmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void BlurBox_PgmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void BlurBox_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(1);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void BlurBox_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(6, 3, NetpbmFormat.PGM_P5);
        var result = img.BlurBox(2);
        Assert.Equal(6, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void BlurBox_UniformImage_PixelStaysUniform()
    {
        // All pixels = 100; after box blur, all should still be 100
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, 100);
        var result = img.BlurBox(1);
        Assert.Equal(100, result.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmBlur_DimsAndFormatUnchanged()
    {
        var img = NetpbmImage.Create(8, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        var result = img.BlurBox(1);
        Assert.Equal(8, result.Width);
        Assert.Equal(5, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void DogfoodPipeline_RadiusOne_ResultIsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(2, 2, 128);
        var result = img.BlurBox(1);
        Assert.NotSame(img, result);
    }
}
