// Tests for NetpbmImage.ApplyGamma dedicated coverage.
// Sprint: ff-sprint-s189-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R185

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R185: Dedicated tests for NetpbmImage.ApplyGamma(double gamma).
/// Applies gamma correction: pixel' = MaxValue * (pixel/MaxValue)^gamma.
/// gamma &lt;= 0 throws ArgumentOutOfRangeException.
/// PBM images return a clone (no change).
/// Returns a new image (not same reference).
/// Format and MaxValue are preserved.
/// Dimensions unchanged.
/// gamma=1.0 is identity: pixel values unchanged.
/// gamma>1.0 darkens; gamma&lt;1.0 brightens (for non-zero pixels).
/// Covers: gamma=0 throws; gamma negative throws; PBM returns new image;
/// PBM format preserved; PGM returns new image; format preserved;
/// MaxValue preserved; dims unchanged; gamma=1.0 identity;
/// dogfood PGM apply gamma dims unchanged.
/// </summary>
public class NetpbmR185ApplyGammaTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_ZeroGamma_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(0.0));
    }

    [Fact]
    public void ApplyGamma_NegativeGamma_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.ApplyGamma(-1.0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_PbmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.ApplyGamma(2.2);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ApplyGamma_PbmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PBM_P4);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(NetpbmFormat.PBM_P4, result.Format);
    }

    [Fact]
    public void ApplyGamma_PgmFormat_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(2.2);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void ApplyGamma_PgmFormat_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void ApplyGamma_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(1.5);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void ApplyGamma_DimensionsUnchanged()
    {
        var img = NetpbmImage.Create(6, 3, NetpbmFormat.PGM_P5);
        var result = img.ApplyGamma(2.0);
        Assert.Equal(6, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void ApplyGamma_GammaOne_PixelValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.ApplyGamma(1.0);
        Assert.Equal(128, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmApplyGamma_DimsAndFormatUnchanged()
    {
        var img = NetpbmImage.Create(8, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        var result = img.ApplyGamma(2.2);
        Assert.Equal(8, result.Width);
        Assert.Equal(5, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void DogfoodPipeline_ZeroPixel_StaysZeroAfterGamma()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0); // 0^gamma = 0
        var result = img.ApplyGamma(2.2);
        Assert.Equal(0, result.GetPixel(0, 0));
    }
}
