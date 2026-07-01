// Tests for NetpbmImage.GetAspectRatio dedicated coverage.
// Sprint: ff-sprint-s401-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R419

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R419: Dedicated tests for NetpbmImage.GetAspectRatio().
/// Returns positive value.
/// Square image returns 1.0.
/// Wider-than-tall returns > 1.0.
/// Taller-than-wide returns less than 1.0.
/// Width unchanged after GetAspectRatio.
/// Height unchanged after GetAspectRatio.
/// Format unchanged after GetAspectRatio.
/// MaxValue unchanged after GetAspectRatio.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM aspect ratio = 1.0.
/// Dogfood: 8x4 PPM aspect ratio = 2.0.
/// </summary>
public class NetpbmR419GetAspectRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio > 0);
    }

    [Fact]
    public void GetAspectRatio_SquareImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double ratio = img.GetAspectRatio();
        Assert.Equal(1.0, ratio, precision: 5);
    }

    [Fact]
    public void GetAspectRatio_WiderThanTall_ReturnsGreaterThanOne()
    {
        var img = NetpbmImage.CreateNew(8, 4, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio > 1.0);
    }

    [Fact]
    public void GetAspectRatio_TallerThanWide_ReturnsLessThanOne()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.True(ratio < 1.0);
    }

    [Fact]
    public void GetAspectRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetAspectRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAspectRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
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
    public void GetAspectRatio_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetAspectRatio();
        double second = img.GetAspectRatio();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_AspectRatioOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double ratio = img.GetAspectRatio();
        Assert.Equal(1.0, ratio, precision: 5);
    }

    [Fact]
    public void DogfoodPipeline_EightByFourPPM_AspectRatioTwo()
    {
        var img = NetpbmImage.CreateNew(8, 4, NetpbmFormat.PPM);
        double ratio = img.GetAspectRatio();
        Assert.Equal(2.0, ratio, precision: 5);
    }
}
