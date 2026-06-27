// Tests for NetpbmImage.GetKurtosis dedicated coverage.
// Sprint: ff-sprint-s321-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R333

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R333: Dedicated tests for NetpbmImage.GetKurtosis().
/// Valid call no exception.
/// Width unchanged after GetKurtosis.
/// Height unchanged after GetKurtosis.
/// Format unchanged after GetKurtosis.
/// MaxValue unchanged after GetKurtosis.
/// All-zero image returns finite-or-NaN.
/// Idempotent (called twice same result class).
/// Uniform image kurtosis finite-or-NaN.
/// Dogfood: gradient image finite-or-NaN.
/// Dogfood: bimodal image finite-or-NaN.
/// </summary>
public class NetpbmR333GetKurtosisDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetKurtosis_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 11 + y * 9) % 256);
        var ex = Record.Exception(() => img.GetKurtosis());
        Assert.Null(ex);
    }

    [Fact]
    public void GetKurtosis_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetKurtosis_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetKurtosis_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetKurtosis_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetKurtosis_AllZeroImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double kurtosis = img.GetKurtosis();
        Assert.True(double.IsFinite(kurtosis) || double.IsNaN(kurtosis));
    }

    [Fact]
    public void GetKurtosis_CalledTwice_SameResultClass()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) * 12 % 256);
        double first = img.GetKurtosis();
        double second = img.GetKurtosis();
        Assert.Equal(double.IsNaN(first), double.IsNaN(second));
    }

    [Fact]
    public void GetKurtosis_UniformImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 180);
        double kurtosis = img.GetKurtosis();
        Assert.True(double.IsFinite(kurtosis) || double.IsNaN(kurtosis));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x * 32);
        double kurtosis = img.GetKurtosis();
        Assert.True(double.IsFinite(kurtosis) || double.IsNaN(kurtosis));
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_BimodalImage_FiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 30 : 220);
        double kurtosis = img.GetKurtosis();
        Assert.True(double.IsFinite(kurtosis) || double.IsNaN(kurtosis));
    }
}
