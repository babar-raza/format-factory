// Tests for NetpbmImage.MedianFilter dedicated coverage.
// Sprint: ff-sprint-s194-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R196

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R196: Dedicated tests for NetpbmImage.MedianFilter(int radius).
/// radius &lt; 0 → throws ArgumentOutOfRangeException.
/// radius == 0 → returns clone (no filtering).
/// radius &gt;= 1 → returns new filtered image.
/// Format, MaxValue, and dimensions are preserved.
/// Uniform image remains uniform after median filter.
/// Covers: negative radius throws; zero radius returns new image;
/// PGM radius=1 returns new image; PGM format preserved; MaxValue preserved;
/// dims unchanged; uniform stays uniform; PBM returns new image;
/// dogfood PGM radius=1 brightness in range; dogfood clone on radius=0 no same reference.
/// </summary>
public class NetpbmR196MedianFilterTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_NegativeRadius_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.MedianFilter(-1));
    }

    // -------------------------------------------------------------------------
    // Radius=0 (clone)
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_ZeroRadius_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(0);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MedianFilter_ZeroRadius_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(0);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    // -------------------------------------------------------------------------
    // PGM radius=1 functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MedianFilter_PgmRadius1_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, (byte)(r * 30 + c * 10));
        var result = img.MedianFilter(1);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void MedianFilter_PgmRadius1_FormatPreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MedianFilter_PgmRadius1_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void MedianFilter_PgmRadius1_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5);
        var result = img.MedianFilter(1);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void MedianFilter_UniformImage_StaysUniform()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(r, c, 128);
        var result = img.MedianFilter(1);
        Assert.Equal(128, result.GetPixel(2, 2));
    }

    [Fact]
    public void MedianFilter_PbmRadius1_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P1);
        var result = img.MedianFilter(1);
        Assert.NotSame(img, result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmGradient_BrightnessInRange()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                img.SetPixel(r, c, (byte)(r * 20 + c * 5));
        var result = img.MedianFilter(1);
        var b = result.GetBrightness();
        Assert.InRange(b, 0.0, 1.0);
    }

    [Fact]
    public void DogfoodPipeline_ZeroRadius_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 100);
        var result = img.MedianFilter(0);
        // Even clone is not same reference
        Assert.False(object.ReferenceEquals(img, result));
        Assert.Equal(100, result.GetPixel(1, 1));
    }
}
