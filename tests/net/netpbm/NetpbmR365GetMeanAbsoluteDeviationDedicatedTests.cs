// Tests for NetpbmImage.GetMeanAbsoluteDeviation dedicated coverage.
// Sprint: ff-sprint-s352-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R365

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R365: Dedicated tests for NetpbmImage.GetMeanAbsoluteDeviation().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetMeanAbsoluteDeviation.
/// Height unchanged after GetMeanAbsoluteDeviation.
/// Format unchanged after GetMeanAbsoluteDeviation.
/// MaxValue unchanged after GetMeanAbsoluteDeviation.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: high-contrast image returns positive MAD.
/// Dogfood: all-zero image returns 0.0.
/// </summary>
public class NetpbmR365GetMeanAbsoluteDeviationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanAbsoluteDeviation_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double mad = img.GetMeanAbsoluteDeviation();
        Assert.True(mad >= 0.0);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        double mad = img.GetMeanAbsoluteDeviation();
        Assert.True(mad >= 0.0);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(100);
        double mad = img.GetMeanAbsoluteDeviation();
        Assert.Equal(0.0, mad, precision: 5);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(75);
        double first = img.GetMeanAbsoluteDeviation();
        double second = img.GetMeanAbsoluteDeviation();
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HighContrast_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double mad = img.GetMeanAbsoluteDeviation();
        Assert.True(mad > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_AllZero_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(0);
        double mad = img.GetMeanAbsoluteDeviation();
        Assert.Equal(0.0, mad, precision: 5);
    }
}
