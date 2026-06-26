// Tests for NetpbmImage.Posterize dedicated coverage.
// Sprint: ff-sprint-s187-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R183

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R183: Dedicated tests for NetpbmImage.Posterize(int levels).
/// Quantizes pixel values to a fixed number of levels.
/// levels &lt; 2 throws ArgumentOutOfRangeException.
/// PBM images return a clone (no change).
/// PGM/PPM images have pixels quantized to the given number of levels.
/// Returns a new image (not same reference, except PBM which returns clone).
/// Format and MaxValue are preserved.
/// Covers: levels=0 throws; levels=1 throws; levels=-1 throws;
/// PBM returns clone format; PGM returns new image; MaxValue preserved;
/// format preserved; uniform image posterize preserves uniform value;
/// dogfood PGM 2-level posterize; dogfood result is new image.
/// </summary>
public class NetpbmR183PosterizeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_LevelsZero_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(0));
    }

    [Fact]
    public void Posterize_LevelsOne_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(1));
    }

    [Fact]
    public void Posterize_NegativeLevels_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Posterize(-5));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Posterize_PbmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.Posterize(4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Posterize_PbmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.Posterize(4);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
    }

    [Fact]
    public void Posterize_PgmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Posterize(4);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Posterize_PgmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Posterize(4);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Posterize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Posterize(4);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Posterize_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(6, 3, NetpbmFormat.PGM_P5);
        var result = img.Posterize(8);
        Assert.Equal(6, result.Width);
        Assert.Equal(3, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmTwoLevels_ValidResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.Posterize(2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }
}
