// Tests for NetpbmImage.GetBinaryThreshold dedicated coverage.
// Sprint: ff-sprint-s413-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R431

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R431: Dedicated tests for NetpbmImage.GetBinaryThreshold().
/// Returns non-negative value.
/// Result within [0, MaxValue].
/// Width unchanged after GetBinaryThreshold.
/// Height unchanged after GetBinaryThreshold.
/// Format unchanged after GetBinaryThreshold.
/// MaxValue unchanged after GetBinaryThreshold.
/// Idempotent (called twice same result).
/// PBM threshold non-negative.
/// PGM threshold non-negative.
/// PPM threshold non-negative.
/// Dogfood: 4x4 PGM threshold within MaxValue.
/// </summary>
public class NetpbmR431GetBinaryThresholdDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBinaryThreshold_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int threshold = img.GetBinaryThreshold();
        Assert.True(threshold >= 0);
    }

    [Fact]
    public void GetBinaryThreshold_WithinMaxValueRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int threshold = img.GetBinaryThreshold();
        Assert.True(threshold <= img.MaxValue);
    }

    [Fact]
    public void GetBinaryThreshold_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetBinaryThreshold();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBinaryThreshold_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetBinaryThreshold();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBinaryThreshold_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetBinaryThreshold();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBinaryThreshold_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetBinaryThreshold();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBinaryThreshold_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetBinaryThreshold();
        int second = img.GetBinaryThreshold();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBinaryThreshold_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetBinaryThreshold() >= 0);
    }

    [Fact]
    public void GetBinaryThreshold_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetBinaryThreshold() >= 0);
    }

    [Fact]
    public void GetBinaryThreshold_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetBinaryThreshold() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ThresholdWithinMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int threshold = img.GetBinaryThreshold();
        Assert.True(threshold >= 0 && threshold <= img.MaxValue);
    }
}
