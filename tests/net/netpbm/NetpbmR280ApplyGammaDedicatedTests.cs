// Tests for NetpbmImage.ApplyGamma dedicated coverage.
// Sprint: ff-sprint-s272-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R280

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R280: Dedicated tests for NetpbmImage.ApplyGamma(gamma).
/// Valid gamma no exception.
/// All pixels remain in [0, MaxValue] after gamma.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice no exception.
/// Uniform image no exception.
/// Dogfood: set pixels, apply gamma, all in range.
/// Dogfood: uniform image, apply gamma, in range.
/// </summary>
public class NetpbmR280ApplyGammaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_ValidGamma_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 128);
        var ex = Record.Exception(() => img.ApplyGamma(2.2));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGamma_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, (c + r * 4) * 16);
        img.ApplyGamma(2.2);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    [Fact]
    public void ApplyGamma_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.ApplyGamma(1.0);
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void ApplyGamma_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.ApplyGamma(1.0);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void ApplyGamma_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        var fmt = img.Format;
        img.ApplyGamma(1.5);
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void ApplyGamma_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 200);
        img.ApplyGamma(2.0);
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void ApplyGamma_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => { img.ApplyGamma(2.2); img.ApplyGamma(1.0); });
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGamma_UniformImage_NoException()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(c, r, 128);
        var ex = Record.Exception(() => img.ApplyGamma(2.2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixelsApplyGamma_AllInRange()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 150);
        img.SetPixel(2, 2, 240);
        img.ApplyGamma(2.2);
        Assert.InRange(img.GetPixel(0, 0), 0, 255);
        Assert.InRange(img.GetPixel(1, 1), 0, 255);
        Assert.InRange(img.GetPixel(2, 2), 0, 255);
    }

    [Fact]
    public void DogfoodPipeline_UniformImageGamma_AllInRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, 180);
        img.ApplyGamma(0.5);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }
}
