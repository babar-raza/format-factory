// Tests for NetpbmImage.GetPixelValueAt dedicated coverage.
// Sprint: ff-sprint-s392-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R410

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R410: Dedicated tests for NetpbmImage.GetPixelValueAt(x, y).
/// Negative x throws.
/// Negative y throws.
/// Out-of-range x throws.
/// Out-of-range y throws.
/// Valid coords return non-negative value.
/// Result within [0, MaxValue].
/// Width unchanged after GetPixelValueAt.
/// Height unchanged after GetPixelValueAt.
/// Format unchanged after GetPixelValueAt.
/// Idempotent (same coords return same value).
/// Dogfood: 2x2 PGM (0,0) in range.
/// </summary>
public class NetpbmR410GetPixelValueAtDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValueAt_NegativeX_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(-1, 0));
    }

    [Fact]
    public void GetPixelValueAt_NegativeY_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(0, -1));
    }

    [Fact]
    public void GetPixelValueAt_OutOfRangeX_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(img.Width, 0));
    }

    [Fact]
    public void GetPixelValueAt_OutOfRangeY_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(0, img.Height));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValueAt_ValidCoords_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int value = img.GetPixelValueAt(0, 0);
        Assert.True(value >= 0);
    }

    [Fact]
    public void GetPixelValueAt_ResultWithinMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int value = img.GetPixelValueAt(0, 0);
        Assert.True(value <= img.MaxValue);
    }

    [Fact]
    public void GetPixelValueAt_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetPixelValueAt(0, 0);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelValueAt_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelValueAt(0, 0);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelValueAt_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelValueAt(0, 0);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelValueAt_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int first = img.GetPixelValueAt(1, 1);
        int second = img.GetPixelValueAt(1, 1);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoByTwoPGM_CornerInRange()
    {
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.PGM);
        int value = img.GetPixelValueAt(0, 0);
        Assert.InRange(value, 0, img.MaxValue);
    }
}
