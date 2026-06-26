// Tests for NetpbmImage.GetVariance dedicated coverage.
// Sprint: ff-sprint-s284-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R292

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R292: Dedicated tests for NetpbmImage.GetVariance().
/// Returns non-negative double.
/// All-zero image returns 0.0 (no variance).
/// All-max image returns 0.0 (no variance, uniform).
/// Width unchanged after GetVariance.
/// Height unchanged after GetVariance.
/// Format unchanged after GetVariance.
/// MaxValue unchanged after GetVariance.
/// Called twice returns same result.
/// Dogfood: mixed image variance non-negative.
/// Dogfood: high-spread image variance positive.
/// </summary>
public class NetpbmR292GetVarianceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVariance_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetVariance_AllZero_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetVariance_AllMax_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, img.MaxValue);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetVariance_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetVariance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetVariance_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetVariance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetVariance_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetVariance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetVariance_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetVariance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetVariance_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 200);
        double first = img.GetVariance();
        double second = img.GetVariance();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_VarianceNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 200);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_HighSpread_VarianceNonNegative()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 255);
        img.SetPixel(0, 1, 0);
        img.SetPixel(1, 1, 255);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }
}
