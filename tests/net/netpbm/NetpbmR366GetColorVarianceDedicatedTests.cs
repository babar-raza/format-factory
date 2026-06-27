// Tests for NetpbmImage.GetColorVariance dedicated coverage.
// Sprint: ff-sprint-s353-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R366

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R366: Dedicated tests for NetpbmImage.GetColorVariance().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetColorVariance.
/// Height unchanged after GetColorVariance.
/// Format unchanged after GetColorVariance.
/// MaxValue unchanged after GetColorVariance.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: varied image returns positive variance.
/// Dogfood: all-zero returns 0.0.
/// </summary>
public class NetpbmR366GetColorVarianceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorVariance_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double variance = img.GetColorVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetColorVariance_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        double variance = img.GetColorVariance();
        Assert.True(variance >= 0.0);
    }

    [Fact]
    public void GetColorVariance_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetColorVariance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetColorVariance_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetColorVariance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetColorVariance_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetColorVariance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetColorVariance_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetColorVariance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetColorVariance_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(150);
        double variance = img.GetColorVariance();
        Assert.Equal(0.0, variance, precision: 5);
    }

    [Fact]
    public void GetColorVariance_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(80);
        double first = img.GetColorVariance();
        double second = img.GetColorVariance();
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_VariedPixels_ReturnsPositiveVariance()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, (r * 4 + c) * 17);
        double variance = img.GetColorVariance();
        Assert.True(variance > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_AllZero_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        double variance = img.GetColorVariance();
        Assert.Equal(0.0, variance, precision: 5);
    }
}
