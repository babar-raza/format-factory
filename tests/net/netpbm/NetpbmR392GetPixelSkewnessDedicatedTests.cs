// Tests for NetpbmImage.GetPixelSkewness dedicated coverage.
// Sprint: ff-sprint-s379-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R392

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R392: Dedicated tests for NetpbmImage.GetPixelSkewness().
/// Valid image returns ok.
/// Width unchanged after GetPixelSkewness.
/// Height unchanged after GetPixelSkewness.
/// Format unchanged after GetPixelSkewness.
/// MaxValue unchanged after GetPixelSkewness.
/// Uniform image returns 0.0 (no asymmetry).
/// Idempotent (called twice same result).
/// Dogfood: asymmetric image returns finite value.
/// Dogfood: gradient image returns finite value.
/// Dogfood: two-value image result is finite.
/// </summary>
public class NetpbmR392GetPixelSkewnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelSkewness_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double skew = img.GetPixelSkewness();
        Assert.True(double.IsFinite(skew) || skew == 0.0);
    }

    [Fact]
    public void GetPixelSkewness_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetPixelSkewness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelSkewness_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelSkewness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelSkewness_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelSkewness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelSkewness_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetPixelSkewness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelSkewness_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 100);
        double skew = img.GetPixelSkewness();
        Assert.Equal(0.0, skew, 6);
    }

    [Fact]
    public void GetPixelSkewness_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 10);
        img.SetPixel(0, 1, 200);
        double first = img.GetPixelSkewness();
        double second = img.GetPixelSkewness();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AsymmetricImage_ReturnsFiniteValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 255);
        img.SetPixel(0, 1, 200);
        // rest zero
        double skew = img.GetPixelSkewness();
        Assert.True(double.IsFinite(skew));
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsFiniteValue()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double skew = img.GetPixelSkewness();
        Assert.True(double.IsFinite(skew));
    }

    [Fact]
    public void DogfoodPipeline_TwoValueImage_ReturnsFiniteValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double skew = img.GetPixelSkewness();
        Assert.True(double.IsFinite(skew));
    }
}
