// Tests for NetpbmImage.GetPixelKurtosis dedicated coverage.
// Sprint: ff-sprint-s380-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R393

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R393: Dedicated tests for NetpbmImage.GetPixelKurtosis().
/// Valid image returns finite value.
/// Width unchanged after GetPixelKurtosis.
/// Height unchanged after GetPixelKurtosis.
/// Format unchanged after GetPixelKurtosis.
/// MaxValue unchanged after GetPixelKurtosis.
/// Uniform image returns defined value.
/// Idempotent (called twice same result).
/// Dogfood: gradient image returns finite value.
/// Dogfood: two-value image returns finite value.
/// Dogfood: mixed image returns finite value.
/// </summary>
public class NetpbmR393GetPixelKurtosisDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelKurtosis_ValidImage_ReturnsFiniteOrDefault()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double kurtosis = img.GetPixelKurtosis();
        Assert.True(double.IsFinite(kurtosis) || kurtosis == 0.0);
    }

    [Fact]
    public void GetPixelKurtosis_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetPixelKurtosis();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelKurtosis_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelKurtosis();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelKurtosis_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelKurtosis();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelKurtosis_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetPixelKurtosis();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelKurtosis_UniformImage_ReturnsDefinedValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 128);
        double kurtosis = img.GetPixelKurtosis();
        // uniform: variance=0, kurtosis undefined but should not throw
        Assert.True(double.IsFinite(kurtosis) || double.IsNaN(kurtosis));
    }

    [Fact]
    public void GetPixelKurtosis_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 10);
        img.SetPixel(0, 1, 200);
        double first = img.GetPixelKurtosis();
        double second = img.GetPixelKurtosis();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsFiniteValue()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double kurtosis = img.GetPixelKurtosis();
        Assert.True(double.IsFinite(kurtosis));
    }

    [Fact]
    public void DogfoodPipeline_TwoValueImage_ReturnsFiniteValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double kurtosis = img.GetPixelKurtosis();
        Assert.True(double.IsFinite(kurtosis));
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_ReturnsFiniteValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 50);
        img.SetPixel(0, 1, 100);
        img.SetPixel(0, 2, 150);
        img.SetPixel(0, 3, 200);
        double kurtosis = img.GetPixelKurtosis();
        Assert.True(double.IsFinite(kurtosis));
    }
}
