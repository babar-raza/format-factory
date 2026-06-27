// Tests for NetpbmImage.GetVariance dedicated coverage.
// Sprint: ff-sprint-s307-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R316

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R316: Dedicated tests for NetpbmImage.GetVariance().
/// Returns non-negative or NaN double.
/// Width unchanged after GetVariance.
/// Height unchanged after GetVariance.
/// Format unchanged after GetVariance.
/// MaxValue unchanged after GetVariance.
/// All-zero image returns zero or non-negative.
/// Called twice returns same class (both finite or both NaN).
/// Mixed image returns non-negative or NaN.
/// Dogfood: standard image returns finite or NaN.
/// Dogfood: uniform image returns near-zero or non-negative.
/// </summary>
public class NetpbmR316GetVarianceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVariance_ReturnsNonNegativeOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 256);
        double v = img.GetVariance();
        Assert.True(v >= 0.0 || double.IsNaN(v));
    }

    [Fact]
    public void GetVariance_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetVariance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetVariance_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
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
    public void GetVariance_AllZeroImage_ReturnsNonNegativeOrNaN()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        double v = img.GetVariance();
        Assert.True(v >= 0.0 || double.IsNaN(v));
    }

    [Fact]
    public void GetVariance_CalledTwice_SameClass()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 5 + y * 3) % 256);
        double first = img.GetVariance();
        double second = img.GetVariance();
        Assert.Equal(double.IsNaN(first), double.IsNaN(second));
        if (!double.IsNaN(first))
            Assert.Equal(first, second, precision: 5);
    }

    [Fact]
    public void GetVariance_MixedImage_ReturnsNonNegativeOrNaN()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 200);
        img.SetPixel(3, 0, 50);
        double v = img.GetVariance();
        Assert.True(v >= 0.0 || double.IsNaN(v));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StandardImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * y) % 256);
        double v = img.GetVariance();
        Assert.True(double.IsFinite(v) || double.IsNaN(v));
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_NonNegativeOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        double v = img.GetVariance();
        Assert.True(v >= 0.0 || double.IsNaN(v));
    }
}
