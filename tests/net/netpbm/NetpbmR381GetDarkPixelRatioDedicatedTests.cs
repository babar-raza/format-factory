// Tests for NetpbmImage.GetDarkPixelRatio dedicated coverage.
// Sprint: ff-sprint-s368-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R381

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R381: Dedicated tests for NetpbmImage.GetDarkPixelRatio().
/// Valid image returns value in [0.0, 1.0].
/// All-white (bright) image returns 0.0.
/// All-black (dark) image returns 1.0.
/// Width unchanged after GetDarkPixelRatio.
/// Height unchanged after GetDarkPixelRatio.
/// Format unchanged after GetDarkPixelRatio.
/// MaxValue unchanged after GetDarkPixelRatio.
/// Idempotent (called twice same result).
/// Dogfood: half-dark image in [0.0, 1.0].
/// Dogfood: single dark pixel in W*H image returns small positive.
/// </summary>
public class NetpbmR381GetDarkPixelRatioDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDarkPixelRatio_ValidImage_InRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double ratio = img.GetDarkPixelRatio();
        Assert.InRange(ratio, 0.0, 1.0);
    }

    [Fact]
    public void GetDarkPixelRatio_AllWhiteImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        double ratio = img.GetDarkPixelRatio();
        Assert.Equal(0.0, ratio, 6);
    }

    [Fact]
    public void GetDarkPixelRatio_AllBlackImage_ReturnsOne()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        double ratio = img.GetDarkPixelRatio();
        Assert.Equal(1.0, ratio, 6);
    }

    [Fact]
    public void GetDarkPixelRatio_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetDarkPixelRatio();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetDarkPixelRatio_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetDarkPixelRatio();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetDarkPixelRatio_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetDarkPixelRatio();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetDarkPixelRatio_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetDarkPixelRatio();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetDarkPixelRatio_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 30);
        double first = img.GetDarkPixelRatio();
        double second = img.GetDarkPixelRatio();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HalfDarkImage_InRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : img.MaxValue);
        double ratio = img.GetDarkPixelRatio();
        Assert.InRange(ratio, 0.0, 1.0);
    }

    [Fact]
    public void DogfoodPipeline_SingleDarkInWhite_ReturnsSmallPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        img.SetPixel(1, 1, 0);
        double ratio = img.GetDarkPixelRatio();
        Assert.True(ratio > 0.0 && ratio < 1.0);
    }
}
