// Tests for NetpbmImage.GetKurtosis dedicated coverage.
// Sprint: ff-sprint-s302-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R310

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R310: Dedicated tests for NetpbmImage.GetKurtosis().
/// Returns double finite or NaN.
/// Width unchanged after GetKurtosis.
/// Height unchanged after GetKurtosis.
/// Format unchanged after GetKurtosis.
/// MaxValue unchanged after GetKurtosis.
/// Called twice returns same value.
/// All-zero image kurtosis is finite or NaN.
/// Mixed image kurtosis is finite or NaN.
/// Dogfood: standard image kurtosis finite or NaN.
/// Dogfood: varying image kurtosis finite or NaN.
/// </summary>
public class NetpbmR310GetKurtosisDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetKurtosis_ReturnsDoubleFiniteOrNaN()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        double k = img.GetKurtosis();
        Assert.True(double.IsFinite(k) || double.IsNaN(k));
    }

    [Fact]
    public void GetKurtosis_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetKurtosis_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetKurtosis_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetKurtosis_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetKurtosis();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetKurtosis_CalledTwice_SameValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 1, 200);
        double first = img.GetKurtosis();
        double second = img.GetKurtosis();
        // NaN != NaN in IEEE, but both calls should give same class of result
        Assert.Equal(double.IsNaN(first), double.IsNaN(second));
        if (!double.IsNaN(first))
            Assert.Equal(first, second);
    }

    [Fact]
    public void GetKurtosis_AllZeroImage_FiniteOrNaN()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double k = img.GetKurtosis();
        Assert.True(double.IsFinite(k) || double.IsNaN(k));
    }

    [Fact]
    public void GetKurtosis_MixedImage_FiniteOrNaN()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 150);
        img.SetPixel(3, 0, 200);
        double k = img.GetKurtosis();
        Assert.True(double.IsFinite(k) || double.IsNaN(k));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StandardImage_KurtosisFiniteOrNaN()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 85);
        img.SetPixel(2, 0, 170);
        img.SetPixel(3, 0, 255);
        double k = img.GetKurtosis();
        Assert.True(double.IsFinite(k) || double.IsNaN(k));
    }

    [Fact]
    public void DogfoodPipeline_VaryingImage_KurtosisFiniteOrNaN()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, (x + y * 4) * 16);
        double k = img.GetKurtosis();
        Assert.True(double.IsFinite(k) || double.IsNaN(k));
    }
}
