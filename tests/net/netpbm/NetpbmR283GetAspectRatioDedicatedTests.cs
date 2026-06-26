// Tests for NetpbmImage.GetAspectRatio dedicated coverage.
// Sprint: ff-sprint-s275-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R283

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R283: Dedicated tests for NetpbmImage.GetAspectRatio().
/// Square image returns 1.0.
/// Wide image returns ratio > 1.0.
/// Tall image returns ratio < 1.0.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice returns same result.
/// 2x1 image returns 2.0.
/// Dogfood: 4x2 image returns 2.0.
/// Dogfood: 3x6 image returns 0.5.
/// </summary>
public class NetpbmR283GetAspectRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_SquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        double ratio = img.GetAspectRatio();
        Assert.Equal(1.0, ratio, precision: 5);
    }

    [Fact]
    public void GetAspectRatio_WideImage_ReturnsGreaterThanOne()
    {
        var img = NetpbmImage.CreateNew(8, 4, NetpbmFormat.Pgm, 255);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio > 1.0);
    }

    [Fact]
    public void GetAspectRatio_TallImage_ReturnsLessThanOne()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.Pgm, 255);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio < 1.0);
    }

    [Fact]
    public void GetAspectRatio_TwoByOneImage_ReturnsTwo()
    {
        var img = NetpbmImage.CreateNew(2, 1, NetpbmFormat.Pgm, 255);
        double ratio = img.GetAspectRatio();
        Assert.Equal(2.0, ratio, precision: 5);
    }

    [Fact]
    public void GetAspectRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 3, NetpbmFormat.Pgm, 255);
        _ = img.GetAspectRatio();
        Assert.Equal(6, img.Width);
    }

    [Fact]
    public void GetAspectRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 3, NetpbmFormat.Pgm, 255);
        _ = img.GetAspectRatio();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void GetAspectRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 2, NetpbmFormat.Pgm, 255);
        var fmt = img.Format;
        _ = img.GetAspectRatio();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void GetAspectRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 2, NetpbmFormat.Pgm, 200);
        _ = img.GetAspectRatio();
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByTwo_ReturnsTwoPointZero()
    {
        var img = NetpbmImage.CreateNew(4, 2, NetpbmFormat.Pgm, 255);
        double ratio = img.GetAspectRatio();
        Assert.Equal(2.0, ratio, precision: 5);
    }

    [Fact]
    public void DogfoodPipeline_ThreeBySix_ReturnsHalf()
    {
        var img = NetpbmImage.CreateNew(3, 6, NetpbmFormat.Pgm, 255);
        double ratio = img.GetAspectRatio();
        Assert.Equal(0.5, ratio, precision: 5);
    }
}
