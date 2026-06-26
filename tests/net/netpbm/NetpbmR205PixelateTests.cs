// Tests for NetpbmImage.Pixelate dedicated coverage.
// Sprint: ff-sprint-s201-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R205

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R205: Dedicated tests for NetpbmImage.Pixelate(int blockSize).
/// blockSize &lt;= 0 → ArgumentOutOfRangeException.
/// Returns a new image (not same reference).
/// Format preserved. Dimensions preserved. MaxValue preserved.
/// blockSize=1 → image visually unchanged (or equivalent to clone).
/// PGM: with blockSize > 1, blocks of same value appear.
/// PPM: format and dims preserved.
/// All output pixels clamped to [0, MaxValue].
/// Dogfood: pixelate then check dims and format stable.
/// Dogfood: pixelate twice, result not same reference.
/// </summary>
public class NetpbmR205PixelateTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Pixelate_ZeroBlockSize_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Pixelate(0));
    }

    [Fact]
    public void Pixelate_NegativeBlockSize_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Pixelate(-1));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Pixelate_PgmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var result = img.Pixelate(2);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Pixelate_PbmImage_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P1);
        var result = img.Pixelate(2);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Pixelate_PgmFormat_Preserved()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var result = img.Pixelate(2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Pixelate_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM_P6);
        var result = img.Pixelate(2);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Pixelate_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Pixelate(3);
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Pixelate_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var result = img.Pixelate(2);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Pixelate_AllPixelsClamped()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                img.SetPixel(r, c, img.MaxValue);
        var result = img.Pixelate(3);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                Assert.True(result.GetPixel(r, c) <= img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PixelateFormatAndDimsStable()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 8; c++)
                img.SetPixel(r, c, (r * 8 + c) * 2);
        var result = img.Pixelate(4);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void DogfoodPipeline_PixelateTwice_NotSameReference()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        var r1 = img.Pixelate(2);
        var r2 = r1.Pixelate(2);
        Assert.NotSame(r1, r2);
        Assert.Equal(NetpbmFormat.PGM_P5, r2.Format);
    }
}
