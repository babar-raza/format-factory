// Tests for NetpbmImage.GetLightPixelRatio dedicated coverage.
// Sprint: ff-sprint-s369-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R382

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R382: Dedicated tests for NetpbmImage.GetLightPixelRatio().
/// Valid image returns value in [0.0, 1.0].
/// All-black image returns 0.0.
/// All-white image returns 1.0.
/// Width unchanged after GetLightPixelRatio.
/// Height unchanged after GetLightPixelRatio.
/// Format unchanged after GetLightPixelRatio.
/// MaxValue unchanged after GetLightPixelRatio.
/// Idempotent (called twice same result).
/// Dogfood: half-light image in [0.0, 1.0].
/// Dogfood: single light pixel in dark image returns small positive.
/// </summary>
public class NetpbmR382GetLightPixelRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLightPixelRatio_ValidImage_InRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double ratio = img.GetLightPixelRatio();
        Assert.InRange(ratio, 0.0, 1.0);
    }

    [Fact]
    public void GetLightPixelRatio_AllBlackImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        double ratio = img.GetLightPixelRatio();
        Assert.Equal(0.0, ratio, 6);
    }

    [Fact]
    public void GetLightPixelRatio_AllWhiteImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        double ratio = img.GetLightPixelRatio();
        Assert.Equal(1.0, ratio, 6);
    }

    [Fact]
    public void GetLightPixelRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetLightPixelRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetLightPixelRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetLightPixelRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetLightPixelRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetLightPixelRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetLightPixelRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetLightPixelRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetLightPixelRatio_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, img.MaxValue);
        double first = img.GetLightPixelRatio();
        double second = img.GetLightPixelRatio();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HalfLightImage_InRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? img.MaxValue : 0);
        double ratio = img.GetLightPixelRatio();
        Assert.InRange(ratio, 0.0, 1.0);
    }

    [Fact]
    public void DogfoodPipeline_SingleLightInDark_ReturnsSmallPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        img.SetPixel(2, 3, img.MaxValue);
        double ratio = img.GetLightPixelRatio();
        Assert.True(ratio > 0.0 && ratio < 1.0);
    }
}
