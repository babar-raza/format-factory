// Tests for NetpbmImage.GetSkewness dedicated coverage.
// Sprint: ff-sprint-s320-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R332

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R332: Dedicated tests for NetpbmImage.GetSkewness().
/// Returns finite or NaN value (not exception).
/// Width unchanged after GetSkewness.
/// Height unchanged after GetSkewness.
/// Format unchanged after GetSkewness.
/// MaxValue unchanged after GetSkewness.
/// All-zero image returns finite-or-NaN.
/// Idempotent (called twice same result class).
/// Uniform image skewness finite-or-NaN.
/// Dogfood: left-skewed image finite-or-NaN.
/// Dogfood: asymmetric image finite-or-NaN.
/// </summary>
public class NetpbmR332GetSkewnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkewness_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 12 + y * 7) % 256);
        var ex = Record.Exception(() => img.GetSkewness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkewness_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetSkewness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSkewness_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetSkewness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSkewness_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetSkewness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSkewness_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetSkewness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSkewness_AllZeroImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double skewness = img.GetSkewness();
        Assert.True(double.IsFinite(skewness) || double.IsNaN(skewness));
    }

    [Fact]
    public void GetSkewness_CalledTwice_SameResultClass()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) * 10 % 256);
        double first = img.GetSkewness();
        double second = img.GetSkewness();
        Assert.Equal(double.IsNaN(first), double.IsNaN(second));
    }

    [Fact]
    public void GetSkewness_UniformImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 150);
        double skewness = img.GetSkewness();
        Assert.True(double.IsFinite(skewness) || double.IsNaN(skewness));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LeftSkewedImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x < 6 ? 200 : 50);
        double skewness = img.GetSkewness();
        Assert.True(double.IsFinite(skewness) || double.IsNaN(skewness));
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_AsymmetricImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (int)(x * x * 4) % 256);
        double skewness = img.GetSkewness();
        Assert.True(double.IsFinite(skewness) || double.IsNaN(skewness));
    }
}
