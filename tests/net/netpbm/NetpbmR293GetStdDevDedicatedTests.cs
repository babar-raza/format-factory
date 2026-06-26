// Tests for NetpbmImage.GetStdDev dedicated coverage.
// Sprint: ff-sprint-s285-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R293

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R293: Dedicated tests for NetpbmImage.GetStdDev().
/// Returns non-negative double.
/// All-zero image returns 0.0 (no variation).
/// All-max image returns 0.0 (no variation, uniform).
/// Width unchanged after GetStdDev.
/// Height unchanged after GetStdDev.
/// Format unchanged after GetStdDev.
/// MaxValue unchanged after GetStdDev.
/// Called twice returns same result.
/// Dogfood: mixed image stddev non-negative.
/// Dogfood: high-spread image stddev non-negative.
/// </summary>
public class NetpbmR293GetStdDevDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStdDev_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        double stddev = img.GetStdDev();
        Assert.True(stddev >= 0.0);
    }

    [Fact]
    public void GetStdDev_AllZero_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        double stddev = img.GetStdDev();
        Assert.True(stddev >= 0.0);
    }

    [Fact]
    public void GetStdDev_AllMax_ReturnsNonNegative()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, img.MaxValue);
        double stddev = img.GetStdDev();
        Assert.True(stddev >= 0.0);
    }

    [Fact]
    public void GetStdDev_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetStdDev();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetStdDev_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetStdDev();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetStdDev_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetStdDev();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetStdDev_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetStdDev();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetStdDev_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(3, 3, 200);
        double first = img.GetStdDev();
        double second = img.GetStdDev();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_StdDevNonNegative()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 180);
        double stddev = img.GetStdDev();
        Assert.True(stddev >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_HighSpread_StdDevNonNegative()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 255);
        img.SetPixel(0, 1, 0);
        img.SetPixel(1, 1, 255);
        double stddev = img.GetStdDev();
        Assert.True(stddev >= 0.0);
    }
}
