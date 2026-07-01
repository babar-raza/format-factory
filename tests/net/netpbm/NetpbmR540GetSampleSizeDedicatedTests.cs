// Tests for NetpbmImage.GetSampleSize dedicated coverage.
// Sprint: ff-sprint-s522-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R540

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R540: Dedicated tests for NetpbmImage.GetSampleSize().
/// PBM image returns positive sample size.
/// PGM image returns positive sample size.
/// PPM image returns positive sample size.
/// Width unchanged after GetSampleSize.
/// Height unchanged after GetSampleSize.
/// Format unchanged after GetSampleSize.
/// MaxValue unchanged after GetSampleSize.
/// Idempotent (called twice same result).
/// Dogfood: PBM sample size positive.
/// Dogfood: PGM sample size positive.
/// Dogfood: PPM sample size positive.
/// </summary>
public class NetpbmR540GetSampleSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSampleSize_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetSampleSize() > 0);
    }

    [Fact]
    public void GetSampleSize_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetSampleSize() > 0);
    }

    [Fact]
    public void GetSampleSize_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetSampleSize() > 0);
    }

    [Fact]
    public void GetSampleSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetSampleSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSampleSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetSampleSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSampleSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetSampleSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSampleSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetSampleSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSampleSize_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetSampleSize();
        int second = img.GetSampleSize();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_SampleSizePositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.True(img.GetSampleSize() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_SampleSizePositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.True(img.GetSampleSize() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_SampleSizePositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.True(img.GetSampleSize() > 0);
    }
}
