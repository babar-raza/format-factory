// Tests for NetpbmImage.GetNonZeroPixelCount dedicated coverage.
// Sprint: ff-sprint-s340-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R353

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R353: Dedicated tests for NetpbmImage.GetNonZeroPixelCount().
/// Valid image ok.
/// Returns non-negative value.
/// Width unchanged after GetNonZeroPixelCount.
/// Height unchanged after GetNonZeroPixelCount.
/// Format unchanged after GetNonZeroPixelCount.
/// MaxValue unchanged after GetNonZeroPixelCount.
/// All-zero image returns 0.
/// Idempotent (called twice same result).
/// Dogfood: uniform non-zero image returns pixel count.
/// Dogfood: single non-zero pixel returns 1.
/// </summary>
public class NetpbmR353GetNonZeroPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNonZeroPixelCount_ValidImage_Ok()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        var ex = Record.Exception(() => img.GetNonZeroPixelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNonZeroPixelCount_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        long count = img.GetNonZeroPixelCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNonZeroPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Width;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetNonZeroPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.Height;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetNonZeroPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        string before = img.Format;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetNonZeroPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(10, 5, 255);
        int before = img.MaxValue;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetNonZeroPixelCount_AllZeroImage_ReturnsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        // All pixels default to 0
        long count = img.GetNonZeroPixelCount();
        Assert.Equal(0L, count);
    }

    [Fact]
    public void GetNonZeroPixelCount_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        img.FillWithValue(100);
        long first = img.GetNonZeroPixelCount();
        long second = img.GetNonZeroPixelCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformNonZeroImage_ReturnsPixelCount()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.FillWithValue(200);
        long count = img.GetNonZeroPixelCount();
        Assert.Equal(16L, count); // 4x4 = 16 pixels all non-zero
    }

    [Fact]
    public void DogfoodPipeline_SingleNonZeroPixel_ReturnsOne()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.SetPixel(2, 2, 128);
        long count = img.GetNonZeroPixelCount();
        Assert.Equal(1L, count);
    }
}
