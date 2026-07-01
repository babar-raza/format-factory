// Tests for NetpbmImage.GetAverageBrightness dedicated coverage.
// Sprint: ff-sprint-s408-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R426

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R426: Dedicated tests for NetpbmImage.GetAverageBrightness().
/// Returns non-negative value.
/// Result within [0, MaxValue].
/// Width unchanged after GetAverageBrightness.
/// Height unchanged after GetAverageBrightness.
/// Format unchanged after GetAverageBrightness.
/// MaxValue unchanged after GetAverageBrightness.
/// Idempotent (called twice same result).
/// PBM average non-negative.
/// PGM average non-negative.
/// PPM average non-negative.
/// Dogfood: 4x4 PGM average non-negative.
/// </summary>
public class NetpbmR426GetAverageBrightnessDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAverageBrightness_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double avg = img.GetAverageBrightness();
        Assert.True(avg >= 0);
    }

    [Fact]
    public void GetAverageBrightness_WithinMaxValueRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double avg = img.GetAverageBrightness();
        Assert.True(avg <= img.MaxValue);
    }

    [Fact]
    public void GetAverageBrightness_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAverageBrightness_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAverageBrightness_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAverageBrightness_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetAverageBrightness();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAverageBrightness_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetAverageBrightness();
        double second = img.GetAverageBrightness();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetAverageBrightness_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetAverageBrightness() >= 0);
    }

    [Fact]
    public void GetAverageBrightness_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetAverageBrightness() >= 0);
    }

    [Fact]
    public void GetAverageBrightness_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetAverageBrightness() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_AverageNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetAverageBrightness() >= 0);
    }
}
