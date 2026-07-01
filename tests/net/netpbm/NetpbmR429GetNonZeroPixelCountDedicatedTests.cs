// Tests for NetpbmImage.GetNonZeroPixelCount dedicated coverage.
// Sprint: ff-sprint-s411-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R429

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R429: Dedicated tests for NetpbmImage.GetNonZeroPixelCount().
/// Returns non-negative value.
/// Result less than or equal to total pixels.
/// Width unchanged after GetNonZeroPixelCount.
/// Height unchanged after GetNonZeroPixelCount.
/// Format unchanged after GetNonZeroPixelCount.
/// MaxValue unchanged after GetNonZeroPixelCount.
/// Idempotent (called twice same result).
/// PBM count non-negative.
/// PGM count non-negative.
/// PPM count non-negative.
/// Dogfood: 4x4 PGM count non-negative.
/// Dogfood: 4x4 PPM count <= total pixels.
/// </summary>
public class NetpbmR429GetNonZeroPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNonZeroPixelCount_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetNonZeroPixelCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNonZeroPixelCount_LessThanOrEqualTotalPixels()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetNonZeroPixelCount();
        Assert.True(count <= img.Width * img.Height);
    }

    [Fact]
    public void GetNonZeroPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetNonZeroPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetNonZeroPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetNonZeroPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetNonZeroPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetNonZeroPixelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetNonZeroPixelCount();
        int second = img.GetNonZeroPixelCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNonZeroPixelCount_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetNonZeroPixelCount() >= 0);
    }

    [Fact]
    public void GetNonZeroPixelCount_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetNonZeroPixelCount() >= 0);
    }

    [Fact]
    public void GetNonZeroPixelCount_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetNonZeroPixelCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_CountNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetNonZeroPixelCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_CountLessOrEqualTotal()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetNonZeroPixelCount() <= img.Width * img.Height);
    }
}
