// Tests for NetpbmImage.GetAspectRatio dedicated coverage.
// Sprint: ff-sprint-s333-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R346

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R346: Dedicated tests for NetpbmImage.GetAspectRatio().
/// Valid image ok.
/// Width and height unchanged after GetAspectRatio.
/// Format unchanged after GetAspectRatio.
/// MaxValue unchanged after GetAspectRatio.
/// Square image returns 1.0.
/// Wide image returns value greater than 1.0.
/// Tall image returns value less than 1.0.
/// Idempotent (called twice same result).
/// Dogfood: 4x2 image returns 2.0.
/// Dogfood: 3x6 image returns 0.5.
/// </summary>
public class NetpbmR346GetAspectRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 4, 255);
        var ex = Record.Exception(() => img.GetAspectRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAspectRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAspectRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAspectRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAspectRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAspectRatio_SquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        double ratio = img.GetAspectRatio();
        Assert.Equal(1.0, ratio, precision: 10);
    }

    [Fact]
    public void GetAspectRatio_WideImage_GreaterThanOne()
    {
        var img = NetpbmImage.CreatePgm(16, 4, 255);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio > 1.0);
    }

    [Fact]
    public void GetAspectRatio_TallImage_LessThanOne()
    {
        var img = NetpbmImage.CreatePgm(4, 16, 255);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio < 1.0);
    }

    [Fact]
    public void GetAspectRatio_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 3, 255);
        double first = img.GetAspectRatio();
        double second = img.GetAspectRatio();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByTwo_ReturnsTwo()
    {
        var img = NetpbmImage.CreatePgm(4, 2, 255);
        double ratio = img.GetAspectRatio();
        Assert.Equal(2.0, ratio, precision: 10);
    }

    [Fact]
    public void DogfoodPipeline_ThreeBySix_ReturnsHalf()
    {
        var img = NetpbmImage.CreatePgm(3, 6, 255);
        double ratio = img.GetAspectRatio();
        Assert.Equal(0.5, ratio, precision: 10);
    }
}
