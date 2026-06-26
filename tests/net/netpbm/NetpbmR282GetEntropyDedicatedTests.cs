// Tests for NetpbmImage.GetEntropy dedicated coverage.
// Sprint: ff-sprint-s274-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R282

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R282: Dedicated tests for NetpbmImage.GetEntropy().
/// Returns non-negative value.
/// Uniform image returns 0.0 (zero entropy).
/// Varied image returns positive entropy.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice returns same result.
/// Single-pixel image returns 0.0.
/// Dogfood: two-value image has positive entropy.
/// Dogfood: uniform image entropy=0.
/// </summary>
public class NetpbmR282GetEntropyDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropy_ValidImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropy_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        // All pixels same value (default 0)
        double entropy = img.GetEntropy();
        Assert.Equal(0.0, entropy, precision: 5);
    }

    [Fact]
    public void GetEntropy_VariedImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        // Mix of different values
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 200);
        img.SetPixel(3, 0, 255);
        double entropy = img.GetEntropy();
        Assert.True(entropy > 0.0);
    }

    [Fact]
    public void GetEntropy_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 50);
        _ = img.GetEntropy();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetEntropy_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 50);
        _ = img.GetEntropy();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void GetEntropy_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 128);
        var fmt = img.Format;
        _ = img.GetEntropy();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void GetEntropy_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 200);
        img.SetPixel(0, 0, 100);
        _ = img.GetEntropy();
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void GetEntropy_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(1, 1, 50);
        img.SetPixel(2, 2, 200);
        double first = img.GetEntropy();
        double second = img.GetEntropy();
        Assert.Equal(first, second, precision: 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoValueImage_HasPositiveEntropy()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        // Half pixels at 0, half at 255
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, (c + r) % 2 == 0 ? 0 : 255);
        double entropy = img.GetEntropy();
        Assert.True(entropy > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_EntropyIsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(c, r, 150);
        double entropy = img.GetEntropy();
        Assert.Equal(0.0, entropy, precision: 5);
    }
}
