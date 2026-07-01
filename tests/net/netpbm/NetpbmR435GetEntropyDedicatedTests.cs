// Tests for NetpbmImage.GetEntropy dedicated coverage.
// Sprint: ff-sprint-s417-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R435

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R435: Dedicated tests for NetpbmImage.GetEntropy().
/// Returns non-negative value.
/// Width unchanged after GetEntropy.
/// Height unchanged after GetEntropy.
/// Format unchanged after GetEntropy.
/// MaxValue unchanged after GetEntropy.
/// Idempotent (called twice same result).
/// PBM entropy non-negative.
/// PGM entropy non-negative.
/// PPM entropy non-negative.
/// Dogfood: 4x4 PGM entropy non-negative.
/// Dogfood: 4x4 PPM entropy non-negative.
/// </summary>
public class NetpbmR435GetEntropyDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEntropy_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double entropy = img.GetEntropy();
        Assert.True(entropy >= 0.0);
    }

    [Fact]
    public void GetEntropy_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEntropy_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEntropy_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetEntropy();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEntropy_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetEntropy();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEntropy_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetEntropy();
        double second = img.GetEntropy();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetEntropy_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetEntropy() >= 0.0);
    }

    [Fact]
    public void GetEntropy_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetEntropy() >= 0.0);
    }

    [Fact]
    public void GetEntropy_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetEntropy() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_EntropyNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetEntropy() >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_EntropyNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetEntropy() >= 0.0);
    }
}
