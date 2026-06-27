// Tests for NetpbmImage.GetHistogramBinCount dedicated coverage.
// Sprint: ff-sprint-s364-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R377

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R377: Dedicated tests for NetpbmImage.GetHistogramBinCount().
/// Valid image returns positive value.
/// Width unchanged after GetHistogramBinCount.
/// Height unchanged after GetHistogramBinCount.
/// Format unchanged after GetHistogramBinCount.
/// MaxValue unchanged after GetHistogramBinCount.
/// Idempotent (called twice same result).
/// All-zero image returns positive.
/// All-max image returns positive.
/// Dogfood: PGM image returns positive.
/// Dogfood: PPM image returns positive.
/// </summary>
public class NetpbmR377GetHistogramBinCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogramBinCount_ValidImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int bins = img.GetHistogramBinCount();
        Assert.True(bins > 0);
    }

    [Fact]
    public void GetHistogramBinCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHistogramBinCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHistogramBinCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHistogramBinCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetHistogramBinCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHistogramBinCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 128);
        int first = img.GetHistogramBinCount();
        int second = img.GetHistogramBinCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetHistogramBinCount_AllZeroImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 0);
        int bins = img.GetHistogramBinCount();
        Assert.True(bins > 0);
    }

    [Fact]
    public void GetHistogramBinCount_AllMaxImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, img.MaxValue);
        int bins = img.GetHistogramBinCount();
        Assert.True(bins > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r * 32 + c * 16) % 256);
        int bins = img.GetHistogramBinCount();
        Assert.True(bins > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, r * 60 + c * 20);
        int bins = img.GetHistogramBinCount();
        Assert.True(bins > 0);
    }
}
