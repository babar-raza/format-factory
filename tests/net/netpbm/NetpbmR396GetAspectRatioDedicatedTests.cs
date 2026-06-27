// Tests for NetpbmImage.GetAspectRatio dedicated coverage.
// Sprint: ff-sprint-s383-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R396

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R396: Dedicated tests for NetpbmImage.GetAspectRatio().
/// Valid image returns positive value.
/// Width unchanged after GetAspectRatio.
/// Height unchanged after GetAspectRatio.
/// Format unchanged after GetAspectRatio.
/// MaxValue unchanged after GetAspectRatio.
/// Square image returns 1.0.
/// Idempotent (called twice same result).
/// Dogfood: 2:1 image returns 2.0.
/// Dogfood: 1:2 image returns 0.5.
/// Dogfood: result is positive.
/// </summary>
public class NetpbmR396GetAspectRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_ValidImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio > 0.0);
    }

    [Fact]
    public void GetAspectRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAspectRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAspectRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAspectRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAspectRatio_SquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.Equal(1.0, ratio, 6);
    }

    [Fact]
    public void GetAspectRatio_Idempotent()
    {
        var img = NetpbmImage.CreateNew(6, 3, NetpbmFormat.PGM);
        double first = img.GetAspectRatio();
        double second = img.GetAspectRatio();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WideImage_ReturnsTwoToOne()
    {
        var img = NetpbmImage.CreateNew(8, 4, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.Equal(2.0, ratio, 6);
    }

    [Fact]
    public void DogfoodPipeline_TallImage_ReturnsHalf()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.Equal(0.5, ratio, 6);
    }

    [Fact]
    public void DogfoodPipeline_AnyImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(7, 3, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio > 0.0);
    }
}
