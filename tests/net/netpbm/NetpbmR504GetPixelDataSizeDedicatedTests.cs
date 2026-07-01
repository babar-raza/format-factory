// Tests for NetpbmImage.GetPixelDataSize dedicated coverage.
// Sprint: ff-sprint-s486-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R504

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R504: Dedicated tests for NetpbmImage.GetPixelDataSize().
/// PBM image returns positive size.
/// PGM image returns positive size.
/// PPM image returns positive size.
/// Width unchanged after GetPixelDataSize.
/// Height unchanged after GetPixelDataSize.
/// Format unchanged after GetPixelDataSize.
/// MaxValue unchanged after GetPixelDataSize.
/// Idempotent (called twice same result).
/// Dogfood: PBM pixel data size is positive.
/// Dogfood: PGM pixel data size is positive.
/// Dogfood: PPM pixel data size is positive.
/// </summary>
public class NetpbmR504GetPixelDataSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelDataSize_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetPixelDataSize() > 0);
    }

    [Fact]
    public void GetPixelDataSize_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetPixelDataSize() > 0);
    }

    [Fact]
    public void GetPixelDataSize_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetPixelDataSize() > 0);
    }

    [Fact]
    public void GetPixelDataSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetPixelDataSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelDataSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetPixelDataSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelDataSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetPixelDataSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelDataSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetPixelDataSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelDataSize_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetPixelDataSize();
        int second = img.GetPixelDataSize();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_SizeIsPositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetPixelDataSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_SizeIsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetPixelDataSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_SizeIsPositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetPixelDataSize();
        Assert.True(result > 0);
    }
}
