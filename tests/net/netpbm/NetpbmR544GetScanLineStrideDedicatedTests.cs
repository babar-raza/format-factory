// Tests for NetpbmImage.GetScanLineStride dedicated coverage.
// Sprint: ff-sprint-s526-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R544

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R544: Dedicated tests for NetpbmImage.GetScanLineStride().
/// PBM image returns positive stride.
/// PGM image returns positive stride.
/// PPM image returns positive stride.
/// Width unchanged after GetScanLineStride.
/// Height unchanged after GetScanLineStride.
/// Format unchanged after GetScanLineStride.
/// MaxValue unchanged after GetScanLineStride.
/// Idempotent (called twice same result).
/// Dogfood: PBM stride positive.
/// Dogfood: PGM stride positive.
/// Dogfood: PPM stride positive.
/// </summary>
public class NetpbmR544GetScanLineStrideDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetScanLineStride_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetScanLineStride() > 0);
    }

    [Fact]
    public void GetScanLineStride_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetScanLineStride() > 0);
    }

    [Fact]
    public void GetScanLineStride_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetScanLineStride() > 0);
    }

    [Fact]
    public void GetScanLineStride_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetScanLineStride();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetScanLineStride_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetScanLineStride();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetScanLineStride_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetScanLineStride();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetScanLineStride_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetScanLineStride();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetScanLineStride_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetScanLineStride();
        int second = img.GetScanLineStride();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_StridePositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        Assert.True(img.GetScanLineStride() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_StridePositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        Assert.True(img.GetScanLineStride() > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_StridePositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        Assert.True(img.GetScanLineStride() > 0);
    }
}
