// Tests for NetpbmImage.GetStdDev dedicated coverage.
// Sprint: ff-sprint-s323-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R335

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R335: Dedicated tests for NetpbmImage.GetStdDev().
/// Valid call no exception.
/// Width unchanged after GetStdDev.
/// Height unchanged after GetStdDev.
/// Format unchanged after GetStdDev.
/// MaxValue unchanged after GetStdDev.
/// Returns non-negative.
/// All-zero image returns zero.
/// Idempotent (called twice same result).
/// Uniform image returns zero.
/// Dogfood: high-contrast image returns positive.
/// </summary>
public class NetpbmR335GetStdDevDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStdDev_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 17 + y * 5) % 256);
        var ex = Record.Exception(() => img.GetStdDev());
        Assert.Null(ex);
    }

    [Fact]
    public void GetStdDev_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetStdDev();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetStdDev_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetStdDev();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetStdDev_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetStdDev();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetStdDev_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetStdDev();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetStdDev_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 13) % 256);
        double stddev = img.GetStdDev();
        Assert.True(stddev >= 0.0);
    }

    [Fact]
    public void GetStdDev_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        double stddev = img.GetStdDev();
        Assert.Equal(0.0, stddev, precision: 10);
    }

    [Fact]
    public void GetStdDev_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 9 + y * 3) % 256);
        double first = img.GetStdDev();
        double second = img.GetStdDev();
        Assert.Equal(first, second, precision: 10);
    }

    [Fact]
    public void GetStdDev_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 200);
        double stddev = img.GetStdDev();
        Assert.Equal(0.0, stddev, precision: 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HighContrastImage_Positive()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 0 : 255);
        double stddev = img.GetStdDev();
        Assert.True(stddev > 0.0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
