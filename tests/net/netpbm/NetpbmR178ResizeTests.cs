// Tests for NetpbmImage.Resize dedicated coverage.
// Sprint: ff-sprint-s182-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R178

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R178: Dedicated tests for NetpbmImage.Resize(int newWidth, int newHeight).
/// Resizes the image using nearest-neighbor interpolation.
/// newWidth &lt;= 0 throws ArgumentOutOfRangeException.
/// newHeight &lt;= 0 throws ArgumentOutOfRangeException.
/// Returns a new image with the specified dimensions.
/// Format and MaxValue are preserved.
/// Covers: zero width throws; negative width throws; zero height throws; negative height throws;
/// returns new image; result width=newWidth; result height=newHeight;
/// format preserved; MaxValue preserved; dogfood scale-up then check dims; dogfood scale-down.
/// </summary>
public class NetpbmR178ResizeTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ZeroWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(0, 4));
    }

    [Fact]
    public void Resize_NegativeWidth_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(-1, 4));
    }

    [Fact]
    public void Resize_ZeroHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(4, 0));
    }

    [Fact]
    public void Resize_NegativeHeight_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Resize(4, -1));
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 8);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Resize_ResultWidth_EqualsNewWidth()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(10, 6);
        Assert.Equal(10, result.Width);
    }

    [Fact]
    public void Resize_ResultHeight_EqualsNewHeight()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(10, 6);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Resize_ResultFormat_MatchesOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 8);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Resize_ResultMaxValue_MatchesOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Resize(8, 8);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ScaleUp_DimsDoubled()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.Resize(8, 6);
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void DogfoodPipeline_ScaleDown_DimsHalved()
    {
        var img = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P5);
        var result = img.Resize(4, 3);
        Assert.Equal(4, result.Width);
        Assert.Equal(3, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }
}
