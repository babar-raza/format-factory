// Tests for NetpbmImage.GetMeanAbsoluteDeviation dedicated coverage.
// Sprint: ff-sprint-s419-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R437

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R437: Dedicated tests for NetpbmImage.GetMeanAbsoluteDeviation().
/// Returns non-negative value.
/// Width unchanged after GetMeanAbsoluteDeviation.
/// Height unchanged after GetMeanAbsoluteDeviation.
/// Format unchanged after GetMeanAbsoluteDeviation.
/// MaxValue unchanged after GetMeanAbsoluteDeviation.
/// Idempotent (called twice same result).
/// PBM mean absolute deviation non-negative.
/// PGM mean absolute deviation non-negative.
/// PPM mean absolute deviation non-negative.
/// Dogfood: 4x4 PGM mean absolute deviation non-negative.
/// Dogfood: 4x4 PPM mean absolute deviation non-negative.
/// </summary>
public class NetpbmR437GetMeanAbsoluteDeviationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanAbsoluteDeviation_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double mad = img.GetMeanAbsoluteDeviation();
        Assert.True(mad >= 0.0);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMeanAbsoluteDeviation();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetMeanAbsoluteDeviation();
        double second = img.GetMeanAbsoluteDeviation();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetMeanAbsoluteDeviation() >= 0.0);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetMeanAbsoluteDeviation() >= 0.0);
    }

    [Fact]
    public void GetMeanAbsoluteDeviation_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetMeanAbsoluteDeviation() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_MADNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetMeanAbsoluteDeviation() >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_MADNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetMeanAbsoluteDeviation() >= 0.0);
    }
}
