// Tests for NetpbmImage.GetPixelDensity dedicated coverage.
// Sprint: ff-sprint-s386-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R399

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R399: Dedicated tests for NetpbmImage.GetPixelDensity().
/// Non-negative result.
/// Width unchanged after GetPixelDensity.
/// Height unchanged after GetPixelDensity.
/// Format unchanged after GetPixelDensity.
/// MaxValue unchanged after GetPixelDensity.
/// Idempotent (called twice same result).
/// PBM pixel density non-negative.
/// PGM pixel density non-negative.
/// PPM pixel density non-negative.
/// Dogfood: 4x4 PBM non-negative.
/// Dogfood: 8x8 PPM non-negative.
/// </summary>
public class NetpbmR399GetPixelDensityDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelDensity_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double density = img.GetPixelDensity();
        Assert.True(density >= 0.0);
    }

    [Fact]
    public void GetPixelDensity_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPixelDensity_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPixelDensity_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPixelDensity_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetPixelDensity();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPixelDensity_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetPixelDensity();
        double second = img.GetPixelDensity();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPixelDensity_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        double density = img.GetPixelDensity();
        Assert.True(density >= 0.0);
    }

    [Fact]
    public void GetPixelDensity_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double density = img.GetPixelDensity();
        Assert.True(density >= 0.0);
    }

    [Fact]
    public void GetPixelDensity_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double density = img.GetPixelDensity();
        Assert.True(density >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        double density = img.GetPixelDensity();
        Assert.True(density >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_EightByEightPPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PPM);
        double density = img.GetPixelDensity();
        Assert.True(density >= 0.0);
    }
}
