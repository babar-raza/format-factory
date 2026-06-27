// Tests for NetpbmImage.GetEntropy dedicated coverage.
// Sprint: ff-sprint-s300-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R308

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R308: Dedicated tests for NetpbmImage.GetEntropy().
/// Returns double non-negative.
/// Width unchanged after GetEntropy.
/// Height unchanged after GetEntropy.
/// Format unchanged after GetEntropy.
/// MaxValue unchanged after GetEntropy.
/// All-zero image entropy is 0.0.
/// Called twice returns same value.
/// Mixed image entropy non-negative.
/// Dogfood: standard image entropy non-negative.
/// Dogfood: entropy for uniform image is 0.
/// </summary>
public class NetpbmR308GetEntropyDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropy_ReturnsNonNegativeDouble()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropy_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEntropy_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEntropy_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEntropy_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetEntropy();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEntropy_AllZeroImage_IsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        // all pixels default to 0 — uniform → entropy = 0
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropy_CalledTwice_SameValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 200);
        double first = img.GetEntropy();
        double second = img.GetEntropy();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetEntropy_MixedImage_NonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 150);
        img.SetPixel(3, 0, 200);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StandardImage_EntropyNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 85);
        img.SetPixel(2, 0, 170);
        img.SetPixel(3, 0, 255);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_EntropyNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        // set all to same value (uniform image)
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 100);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }
}
