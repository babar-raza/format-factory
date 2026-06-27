// Tests for NetpbmImage.GetStandardDeviation dedicated coverage.
// Sprint: ff-sprint-s351-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R364

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R364: Dedicated tests for NetpbmImage.GetStandardDeviation().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetStandardDeviation.
/// Height unchanged after GetStandardDeviation.
/// Format unchanged after GetStandardDeviation.
/// MaxValue unchanged after GetStandardDeviation.
/// Uniform image returns 0.0.
/// Idempotent (called twice same result).
/// Dogfood: half-0 half-255 image returns positive std dev.
/// Dogfood: all-128 image returns 0.0.
/// </summary>
public class NetpbmR364GetStandardDeviationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStandardDeviation_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_ResultIsNonNegative()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PPM, 255);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetStandardDeviation_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetStandardDeviation_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM, 255);
        var before = img.Format;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetStandardDeviation_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 200);
        int before = img.MaxValue;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetStandardDeviation_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(128);
        double sd = img.GetStandardDeviation();
        Assert.Equal(0.0, sd, precision: 5);
    }

    [Fact]
    public void GetStandardDeviation_Idempotent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM, 255);
        img.FillWithValue(64);
        double first = img.GetStandardDeviation();
        double second = img.GetStandardDeviation();
        Assert.Equal(first, second, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HalfZeroHalfMax_ReturnsPositive()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 4; c++)
                img.SetPixel(r, c, (r * 4 + c) < 8 ? 0 : 255);
        double sd = img.GetStandardDeviation();
        Assert.True(sd > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_All128_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.FillWithValue(128);
        double sd = img.GetStandardDeviation();
        Assert.Equal(0.0, sd, precision: 5);
    }
}
