// Tests for NetpbmImage.GetPixelEntropy dedicated coverage.
// Sprint: ff-sprint-s373-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R386

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R386: Dedicated tests for NetpbmImage.GetPixelEntropy().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetPixelEntropy.
/// Height unchanged after GetPixelEntropy.
/// Format unchanged after GetPixelEntropy.
/// MaxValue unchanged after GetPixelEntropy.
/// Uniform image returns 0.0 (no information).
/// Idempotent (called twice same result).
/// Dogfood: two-value image returns positive entropy.
/// Dogfood: gradient image returns positive entropy.
/// </summary>
public class NetpbmR386GetPixelEntropyDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelEntropy_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double entropy = img.GetPixelEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetPixelEntropy_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        double entropy = img.GetPixelEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetPixelEntropy_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetPixelEntropy();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelEntropy_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelEntropy();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelEntropy_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelEntropy();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelEntropy_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetPixelEntropy();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelEntropy_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 128);
        double entropy = img.GetPixelEntropy();
        Assert.Equal(0.0, entropy, 6);
    }

    [Fact]
    public void GetPixelEntropy_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 255);
        double first = img.GetPixelEntropy();
        double second = img.GetPixelEntropy();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoValueImage_ReturnsPositiveEntropy()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double entropy = img.GetPixelEntropy();
        Assert.True(entropy > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsPositiveEntropy()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double entropy = img.GetPixelEntropy();
        Assert.True(entropy > 0.0);
    }
}
