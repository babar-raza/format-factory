// Tests for NetpbmImage.GetPixelIntensity dedicated coverage.
// Sprint: ff-sprint-s405-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R423

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R423: Dedicated tests for NetpbmImage.GetPixelIntensity(x, y).
/// Negative x throws.
/// Negative y throws.
/// Out-of-range x throws.
/// Out-of-range y throws.
/// Valid pixel returns non-negative value.
/// Result within MaxValue range.
/// Width unchanged after GetPixelIntensity.
/// Height unchanged after GetPixelIntensity.
/// Format unchanged after GetPixelIntensity.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM corner pixel non-negative.
/// </summary>
public class NetpbmR423GetPixelIntensityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelIntensity_NegativeX_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelIntensity(-1, 0));
    }

    [Fact]
    public void GetPixelIntensity_NegativeY_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelIntensity(0, -1));
    }

    [Fact]
    public void GetPixelIntensity_OutOfRangeX_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelIntensity(img.Width, 0));
    }

    [Fact]
    public void GetPixelIntensity_OutOfRangeY_Throws()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.ThrowsAny<Exception>(() => img.GetPixelIntensity(0, img.Height));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelIntensity_ValidPixel_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int intensity = img.GetPixelIntensity(0, 0);
        Assert.True(intensity >= 0);
    }

    [Fact]
    public void GetPixelIntensity_ResultWithinMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int intensity = img.GetPixelIntensity(0, 0);
        Assert.True(intensity <= img.MaxValue);
    }

    [Fact]
    public void GetPixelIntensity_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetPixelIntensity(0, 0);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelIntensity_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelIntensity(0, 0);
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelIntensity_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelIntensity(0, 0);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelIntensity_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int first = img.GetPixelIntensity(0, 0);
        int second = img.GetPixelIntensity(0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_CornerPixelNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int intensity = img.GetPixelIntensity(0, 0);
        Assert.True(intensity >= 0);
    }
}
