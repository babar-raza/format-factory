// Tests for NetpbmImage.ApplyGaussianBlur dedicated coverage.
// Sprint: ff-sprint-s297-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R305

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R305: Dedicated tests for NetpbmImage.ApplyGaussianBlur(radius).
/// Valid call no exception.
/// All pixels in [0, MaxValue] after blur.
/// Width unchanged after ApplyGaussianBlur.
/// Height unchanged after ApplyGaussianBlur.
/// Format unchanged after ApplyGaussianBlur.
/// MaxValue unchanged after ApplyGaussianBlur.
/// Called twice no exception.
/// Radius of 1 no exception.
/// Dogfood: blur and verify pixels in range.
/// Dogfood: blur mixed image pixels in range.
/// </summary>
public class NetpbmR305ApplyGaussianBlurDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGaussianBlur_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.ApplyGaussianBlur(1));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGaussianBlur_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(3, 3, 255);
        img.ApplyGaussianBlur(1);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplyGaussianBlur_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyGaussianBlur(1);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyGaussianBlur_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyGaussianBlur(1);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyGaussianBlur_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyGaussianBlur(1);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyGaussianBlur_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyGaussianBlur(1);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyGaussianBlur_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.ApplyGaussianBlur(1);
        var ex = Record.Exception(() => img.ApplyGaussianBlur(1));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGaussianBlur_RadiusOne_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 200);
        var ex = Record.Exception(() => img.ApplyGaussianBlur(1));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_BlurAndVerifyPixelsInRange()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM, 255);
        img.SetPixel(3, 3, 200);
        img.ApplyGaussianBlur(2);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_BlurredPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 150);
        img.SetPixel(2, 0, 200);
        img.SetPixel(3, 0, 255);
        img.ApplyGaussianBlur(1);
        for (int x = 0; x < 4; x++)
            Assert.InRange(img.GetPixel(x, 0), 0, img.MaxValue);
    }
}
