// Tests for NetpbmImage.GetZeroPixelCount dedicated coverage.
// Sprint: ff-sprint-s412-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R430

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R430: Dedicated tests for NetpbmImage.GetZeroPixelCount().
/// Returns non-negative value.
/// Result less than or equal to total pixels.
/// Width unchanged after GetZeroPixelCount.
/// Height unchanged after GetZeroPixelCount.
/// Format unchanged after GetZeroPixelCount.
/// MaxValue unchanged after GetZeroPixelCount.
/// Idempotent (called twice same result).
/// PBM count non-negative.
/// PGM count non-negative.
/// PPM count non-negative.
/// Dogfood: 4x4 PGM count + non-zero count = total pixels.
/// </summary>
public class NetpbmR430GetZeroPixelCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZeroPixelCount_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetZeroPixelCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetZeroPixelCount_LessThanOrEqualTotalPixels()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int count = img.GetZeroPixelCount();
        Assert.True(count <= img.Width * img.Height);
    }

    [Fact]
    public void GetZeroPixelCount_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetZeroPixelCount();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetZeroPixelCount_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetZeroPixelCount();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetZeroPixelCount_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetZeroPixelCount();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetZeroPixelCount_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetZeroPixelCount();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetZeroPixelCount_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetZeroPixelCount();
        int second = img.GetZeroPixelCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetZeroPixelCount_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetZeroPixelCount() >= 0);
    }

    [Fact]
    public void GetZeroPixelCount_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetZeroPixelCount() >= 0);
    }

    [Fact]
    public void GetZeroPixelCount_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetZeroPixelCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ZeroAndNonZeroSumToTotal()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int total = img.Width * img.Height;
        int zero = img.GetZeroPixelCount();
        int nonZero = img.GetNonZeroPixelCount();
        Assert.Equal(total, zero + nonZero);
    }
}
