// Tests for NetpbmImage.GetRowDataSize dedicated coverage.
// Sprint: ff-sprint-s487-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R505

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R505: Dedicated tests for NetpbmImage.GetRowDataSize().
/// PBM image row data size is positive.
/// PGM image row data size is positive.
/// PPM image row data size is positive.
/// Width unchanged after GetRowDataSize.
/// Height unchanged after GetRowDataSize.
/// Format unchanged after GetRowDataSize.
/// MaxValue unchanged after GetRowDataSize.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline row size is positive.
/// Dogfood: PGM pipeline row size is positive.
/// Dogfood: PPM pipeline row size is positive.
/// </summary>
public class NetpbmR505GetRowDataSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowDataSize_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(8, 4);
        Assert.True(img.GetRowDataSize() > 0);
    }

    [Fact]
    public void GetRowDataSize_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 4, 255);
        Assert.True(img.GetRowDataSize() > 0);
    }

    [Fact]
    public void GetRowDataSize_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(8, 4, 255);
        Assert.True(img.GetRowDataSize() > 0);
    }

    [Fact]
    public void GetRowDataSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetRowDataSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetRowDataSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetRowDataSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetRowDataSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetRowDataSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetRowDataSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetRowDataSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetRowDataSize_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetRowDataSize();
        int second = img.GetRowDataSize();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_RowSizeIsPositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetRowDataSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_RowSizeIsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetRowDataSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_RowSizeIsPositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetRowDataSize();
        Assert.True(result > 0);
    }
}
