// Tests for NetpbmImage.GetEntropy dedicated coverage.
// Sprint: ff-sprint-s319-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R330

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R330: Dedicated tests for NetpbmImage.GetEntropy().
/// Returns non-negative value.
/// Width unchanged after GetEntropy.
/// Height unchanged after GetEntropy.
/// Format unchanged after GetEntropy.
/// MaxValue unchanged after GetEntropy.
/// All-zero image returns non-negative entropy.
/// Idempotent (called twice same result).
/// Uniform image entropy in expected range.
/// Dogfood: mixed image entropy non-negative.
/// Dogfood: high-entropy image entropy non-negative.
/// </summary>
public class NetpbmR330GetEntropyDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropy_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 17 + y * 13) % 256);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropy_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEntropy_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEntropy_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEntropy_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetEntropy();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEntropy_AllZeroImage_NonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropy_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) * 14 % 256);
        double first = img.GetEntropy();
        double second = img.GetEntropy();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetEntropy_UniformImage_NonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_EntropyNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * y * 3 + 7) % 256);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_HighEntropyImage_EntropyNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 11 + 3) % 256);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }
}
