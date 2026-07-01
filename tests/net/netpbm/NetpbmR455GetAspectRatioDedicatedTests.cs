// Tests for NetpbmImage.GetAspectRatio dedicated coverage.
// Sprint: ff-sprint-s437-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R455

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R455: Dedicated tests for NetpbmImage.GetAspectRatio().
/// Returns positive value for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Square image returns 1.0.
/// Dogfood: 4x4 PGM and PPM aspect ratio equals 1.0.
/// </summary>
public class NetpbmR455GetAspectRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetAspectRatio();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetAspectRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAspectRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAspectRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAspectRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAspectRatio_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetAspectRatio();
        double second = img.GetAspectRatio();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetAspectRatio_SquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetAspectRatio();
        Assert.Equal(1.0, val, precision: 5);
    }

    [Fact]
    public void GetAspectRatio_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetAspectRatio();
        Assert.True(val > 0.0);
    }

    [Fact]
    public void GetAspectRatio_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetAspectRatio();
        Assert.True(val > 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_AspectRatioIsOne()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetAspectRatio();
        Assert.Equal(1.0, val, precision: 5);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_AspectRatioIsOne()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetAspectRatio();
        Assert.Equal(1.0, val, precision: 5);
    }
}
