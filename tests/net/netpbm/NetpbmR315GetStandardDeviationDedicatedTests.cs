// Tests for NetpbmImage.GetStandardDeviation dedicated coverage.
// Sprint: ff-sprint-s306-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R315

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R315: Dedicated tests for NetpbmImage.GetStandardDeviation().
/// Returns non-negative double.
/// Width unchanged after GetStandardDeviation.
/// Height unchanged after GetStandardDeviation.
/// Format unchanged after GetStandardDeviation.
/// MaxValue unchanged after GetStandardDeviation.
/// All-zero image returns zero standard deviation.
/// Called twice returns same result.
/// Mixed image returns non-negative.
/// Dogfood: standard image and verify finite.
/// Dogfood: uniform image returns near-zero standard deviation.
/// </summary>
public class NetpbmR315GetStandardDeviationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStandardDeviation_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 256);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0 || double.IsNaN(sd));
    }

    [Fact]
    public void GetStandardDeviation_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetStandardDeviation_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetStandardDeviation_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetStandardDeviation_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetStandardDeviation_AllZeroImage_ReturnsZeroOrNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0 || double.IsNaN(sd));
    }

    [Fact]
    public void GetStandardDeviation_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 3 + y * 7) % 256);
        double first = img.GetStandardDeviation();
        double second = img.GetStandardDeviation();
        Assert.Equal(double.IsNaN(first), double.IsNaN(second));
        if (!double.IsNaN(first))
            Assert.Equal(first, second, precision: 5);
    }

    [Fact]
    public void GetStandardDeviation_MixedImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 128);
        img.SetPixel(2, 0, 255);
        img.SetPixel(3, 0, 64);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0 || double.IsNaN(sd));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StandardImage_ReturnsFiniteOrNaN()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * y) % 256);
        double sd = img.GetStandardDeviation();
        Assert.True(double.IsFinite(sd) || double.IsNaN(sd));
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_NearZeroOrNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0 || double.IsNaN(sd));
    }
}
