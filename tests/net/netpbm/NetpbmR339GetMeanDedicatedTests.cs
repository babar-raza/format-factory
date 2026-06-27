// Tests for NetpbmImage.GetMean dedicated coverage.
// Sprint: ff-sprint-s327-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R339

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R339: Dedicated tests for NetpbmImage.GetMean().
/// Valid call no exception.
/// Width unchanged after GetMean.
/// Height unchanged after GetMean.
/// Format unchanged after GetMean.
/// MaxValue unchanged after GetMean.
/// Returns value in [0, MaxValue].
/// All-zero image returns zero mean.
/// Idempotent (called twice same result).
/// Uniform image mean equals pixel value.
/// Dogfood: gradient image mean is non-negative.
/// </summary>
public class NetpbmR339GetMeanDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMean_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 11 + y * 7) % 256);
        var ex = Record.Exception(() => img.GetMean());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMean_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMean();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMean_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMean();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMean_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMean();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMean_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMean();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMean_ReturnsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 5 + y * 9) % 256);
        double mean = img.GetMean();
        Assert.InRange(mean, 0.0, img.MaxValue);
    }

    [Fact]
    public void GetMean_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double mean = img.GetMean();
        Assert.Equal(0.0, mean, precision: 10);
    }

    [Fact]
    public void GetMean_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 3 + y * 11) % 256);
        double first = img.GetMean();
        double second = img.GetMean();
        Assert.Equal(first, second, precision: 10);
    }

    [Fact]
    public void GetMean_UniformImage_MeanEqualsPixelValue()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 150);
        double mean = img.GetMean();
        Assert.Equal(150.0, mean, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_MeanNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x * 32);
        double mean = img.GetMean();
        Assert.True(mean >= 0.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
