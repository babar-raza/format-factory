// Tests for NetpbmImage.GetTotalFileSize dedicated coverage.
// Sprint: ff-sprint-s490-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R508

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R508: Dedicated tests for NetpbmImage.GetTotalFileSize().
/// PBM image total file size is positive.
/// PGM image total file size is positive.
/// PPM image total file size is positive.
/// Width unchanged after GetTotalFileSize.
/// Height unchanged after GetTotalFileSize.
/// Format unchanged after GetTotalFileSize.
/// MaxValue unchanged after GetTotalFileSize.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline total file size is positive.
/// Dogfood: PGM pipeline total file size is positive.
/// Dogfood: PPM pipeline total file size is positive.
/// </summary>
public class NetpbmR508GetTotalFileSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTotalFileSize_PbmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetTotalFileSize() > 0);
    }

    [Fact]
    public void GetTotalFileSize_PgmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetTotalFileSize() > 0);
    }

    [Fact]
    public void GetTotalFileSize_PpmImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetTotalFileSize() > 0);
    }

    [Fact]
    public void GetTotalFileSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetTotalFileSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetTotalFileSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetTotalFileSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetTotalFileSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetTotalFileSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetTotalFileSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetTotalFileSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetTotalFileSize_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        int first = img.GetTotalFileSize();
        int second = img.GetTotalFileSize();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_TotalFileSizeIsPositive()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        int result = img.GetTotalFileSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_TotalFileSizeIsPositive()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        int result = img.GetTotalFileSize();
        Assert.True(result > 0);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_TotalFileSizeIsPositive()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        int result = img.GetTotalFileSize();
        Assert.True(result > 0);
    }
}
