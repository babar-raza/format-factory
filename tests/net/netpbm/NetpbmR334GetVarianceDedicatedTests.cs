// Tests for NetpbmImage.GetVariance dedicated coverage.
// Sprint: ff-sprint-s322-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R334

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R334: Dedicated tests for NetpbmImage.GetVariance().
/// Valid call no exception.
/// Width unchanged after GetVariance.
/// Height unchanged after GetVariance.
/// Format unchanged after GetVariance.
/// MaxValue unchanged after GetVariance.
/// Returns non-negative.
/// All-zero image returns zero variance.
/// Idempotent (called twice same result).
/// Uniform image returns zero variance.
/// Dogfood: gradient image variance is non-negative.
/// </summary>
public class NetpbmR334GetVarianceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVariance_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 13 + y * 7) % 256);
        var ex = Record.Exception(() => img.GetVariance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetVariance_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetVariance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetVariance_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetVariance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetVariance_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetVariance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetVariance_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetVariance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetVariance_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y * 3) % 256);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetVariance_AllZeroImage_ZeroVariance()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double variance = img.GetVariance();
        Assert.Equal(0.0, variance, precision: 10);
    }

    [Fact]
    public void GetVariance_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 5 + y * 11) % 256);
        double first = img.GetVariance();
        double second = img.GetVariance();
        Assert.Equal(first, second, precision: 10);
    }

    [Fact]
    public void GetVariance_UniformImage_ZeroVariance()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        double variance = img.GetVariance();
        Assert.Equal(0.0, variance, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_NonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x * 32);
        double variance = img.GetVariance();
        Assert.True(variance >= 0.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
