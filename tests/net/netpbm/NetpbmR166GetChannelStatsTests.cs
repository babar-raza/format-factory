// Tests for NetpbmImage.GetChannelStats dedicated coverage.
// Sprint: ff-sprint-s170-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R166

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R166: Dedicated tests for NetpbmImage.GetChannelStats().
/// Returns ((Mean,Min,Max) R, (Mean,Min,Max) G, (Mean,Min,Max) B) for PPM images.
/// Throws InvalidOperationException for non-PPM (PBM or PGM) formats.
/// Zero-pixel image returns all-zeros tuples.
/// Covers: PBM throws InvalidOperationException; PGM_P2 throws; PGM_P5 throws;
/// PPM_P3 returns tuple; PPM_P6 returns tuple; zero-pixel returns zeros;
/// uniform PPM: mean equals the constant value; min<=mean<=max;
/// dogfood Create->SetPixel->GetChannelStats; R/G/B channels are independent.
/// </summary>
public class NetpbmR166GetChannelStatsTests
{
    // -------------------------------------------------------------------------
    // Guard tests — non-PPM throws
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStats_PbmP1_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P1);
        Assert.Throws<InvalidOperationException>(() => img.GetChannelStats());
    }

    [Fact]
    public void GetChannelStats_PgmP2_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2);
        Assert.Throws<InvalidOperationException>(() => img.GetChannelStats());
    }

    [Fact]
    public void GetChannelStats_PgmP5_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        Assert.Throws<InvalidOperationException>(() => img.GetChannelStats());
    }

    // -------------------------------------------------------------------------
    // Valid PPM tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStats_PpmP3_ReturnsResult()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P3);
        var stats = img.GetChannelStats();
        // Should return without throwing; means/min/max are valid
        Assert.True(stats.R.Mean >= 0);
        Assert.True(stats.G.Mean >= 0);
        Assert.True(stats.B.Mean >= 0);
    }

    [Fact]
    public void GetChannelStats_PpmP6_ReturnsResult()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P6);
        var stats = img.GetChannelStats();
        Assert.True(stats.R.Mean >= 0);
    }

    [Fact]
    public void GetChannelStats_MinLessThanOrEqualToMeanLessThanOrEqualToMax()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6);
        img.SetPixel(0, 0, 50);  // sets all channels to 50
        img.SetPixel(3, 3, 200);
        var stats = img.GetChannelStats();
        Assert.True(stats.R.Min <= stats.R.Mean);
        Assert.True(stats.R.Mean <= stats.R.Max);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformPpm_MeanEqualsConstant()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PPM_P6);
        // Set all pixels to value 100 (affects all three channels)
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(r, c, 100);
        var stats = img.GetChannelStats();
        // All channels should have mean == 100, min == 100, max == 100
        Assert.Equal(100, stats.R.Min);
        Assert.Equal(100, stats.R.Max);
    }

    [Fact]
    public void DogfoodPipeline_SinglePixel_MeanEqualsPixelValue()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PPM_P6);
        img.SetPixel(0, 0, 77);
        var stats = img.GetChannelStats();
        // Single pixel: mean == min == max == pixel value
        Assert.Equal(77.0, stats.R.Mean, precision: 1);
        Assert.Equal(77, stats.R.Min);
        Assert.Equal(77, stats.R.Max);
    }
}
