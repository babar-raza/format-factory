// Tests for NetpbmImage.GetHeaderSize dedicated coverage.
// Sprint: ff-sprint-s489-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R507

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R507: Dedicated tests for NetpbmImage.GetHeaderSize().
/// PBM image header size is positive.
/// PGM image header size is positive.
/// PPM image header size is positive.
/// Width unchanged after GetHeaderSize.
/// Height unchanged after GetHeaderSize.
/// Format unchanged after GetHeaderSize.
/// MaxValue unchanged after GetHeaderSize.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline header size is positive.
/// Dogfood: PGM pipeline header size is positive.
/// Dogfood: PPM pipeline header size is positive.
/// </summary>
public class NetpbmR507GetHeaderSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaderSize_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetHeaderSize() > 0);
    }

    [Fact]
    public void GetHeaderSize_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetHeaderSize() > 0);
    }

    [Fact]
    public void GetHeaderSize_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetHeaderSize() > 0);
    }

    [Fact]
    public void GetHeaderSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetHeaderSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHeaderSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetHeaderSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHeaderSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetHeaderSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHeaderSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetHeaderSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHeaderSize_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetHeaderSize();
        int second = img.GetHeaderSize();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_HeaderSizeIsPositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetHeaderSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_HeaderSizeIsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetHeaderSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_HeaderSizeIsPositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetHeaderSize();
        Assert.True(result > 0);
    }
}
