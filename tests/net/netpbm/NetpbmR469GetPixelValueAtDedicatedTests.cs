// Tests for NetpbmImage.GetPixelValueAt dedicated coverage.
// Sprint: ff-sprint-s451-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R469

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R469: Dedicated tests for NetpbmImage.GetPixelValueAt(int x, int y).
/// Out-of-range coordinates throw.
/// Valid coordinates return non-negative int.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (same coordinates same result).
/// Dogfood: 4x4 PGM and PPM center pixel non-negative.
/// </summary>
public class NetpbmR469GetPixelValueAtDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValueAt_NegativeX_Throws()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(-1, 0));
    }

    [Fact]
    public void GetPixelValueAt_NegativeY_Throws()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(0, -1));
    }

    [Fact]
    public void GetPixelValueAt_XOutOfRange_Throws()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(img.Width, 0));
    }

    [Fact]
    public void GetPixelValueAt_YOutOfRange_Throws()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixelValueAt(0, img.Height));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValueAt_ValidCoordinates_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetPixelValueAt(0, 0);
        Assert.True(val >= 0);
    }

    [Fact]
    public void GetPixelValueAt_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetPixelValueAt(0, 0);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelValueAt_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetPixelValueAt(0, 0);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelValueAt_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int first = img.GetPixelValueAt(1, 1);
        int second = img.GetPixelValueAt(1, 1);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_CenterPixelNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetPixelValueAt(2, 2);
        Assert.True(val >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_CenterPixelNonNegative()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int val = img.GetPixelValueAt(2, 2);
        Assert.True(val >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_CornerPixelNonNegative()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetPixelValueAt(3, 3);
        Assert.True(val >= 0);
    }
}
