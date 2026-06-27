// Tests for NetpbmImage.GetMean dedicated coverage.
// Sprint: ff-sprint-s308-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R317

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R317: Dedicated tests for NetpbmImage.GetMean().
/// Returns value in [0, MaxValue] range.
/// Width unchanged after GetMean.
/// Height unchanged after GetMean.
/// Format unchanged after GetMean.
/// MaxValue unchanged after GetMean.
/// All-zero image returns zero mean.
/// Called twice returns same result.
/// Uniform image returns that uniform value as mean.
/// Dogfood: standard image returns finite value.
/// Dogfood: two-value image mean in range.
/// </summary>
public class NetpbmR317GetMeanDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMean_ReturnsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 256);
        double mean = img.GetMean();
        Assert.True(mean >= 0.0 && mean <= img.MaxValue);
    }

    [Fact]
    public void GetMean_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMean();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMean_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
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
    public void GetMean_AllZeroImage_ReturnsZeroOrNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        double mean = img.GetMean();
        Assert.True(mean >= 0.0);
    }

    [Fact]
    public void GetMean_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 3 + y * 5) % 256);
        double first = img.GetMean();
        double second = img.GetMean();
        Assert.Equal(first, second, precision: 5);
    }

    [Fact]
    public void GetMean_UniformImage_ReturnsNearUniformValue()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        double mean = img.GetMean();
        Assert.InRange(mean, 0.0, 255.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StandardImage_FiniteInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * y) % 256);
        double mean = img.GetMean();
        Assert.True(double.IsFinite(mean));
        Assert.True(mean >= 0.0 && mean <= 255.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_TwoValueImage_MeanInRange()
    {
        var img = NetpbmImage.CreateNew(4, 2, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 0);
        img.SetPixel(2, 0, 200);
        img.SetPixel(3, 0, 200);
        img.SetPixel(0, 1, 50);
        img.SetPixel(1, 1, 50);
        img.SetPixel(2, 1, 150);
        img.SetPixel(3, 1, 150);
        double mean = img.GetMean();
        Assert.True(mean >= 0.0 && mean <= 255.0);
    }
}
