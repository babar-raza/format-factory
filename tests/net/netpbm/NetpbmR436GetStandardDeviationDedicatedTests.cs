// Tests for NetpbmImage.GetStandardDeviation dedicated coverage.
// Sprint: ff-sprint-s418-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R436

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R436: Dedicated tests for NetpbmImage.GetStandardDeviation().
/// Returns non-negative value.
/// Width unchanged after GetStandardDeviation.
/// Height unchanged after GetStandardDeviation.
/// Format unchanged after GetStandardDeviation.
/// MaxValue unchanged after GetStandardDeviation.
/// Idempotent (called twice same result).
/// PBM standard deviation non-negative.
/// PGM standard deviation non-negative.
/// PPM standard deviation non-negative.
/// Dogfood: 4x4 PGM standard deviation non-negative.
/// Dogfood: 4x4 PPM standard deviation non-negative.
/// </summary>
public class NetpbmR436GetStandardDeviationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStandardDeviation_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double sd = img.GetStandardDeviation();
        Assert.True(sd >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetStandardDeviation_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetStandardDeviation_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetStandardDeviation_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetStandardDeviation();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetStandardDeviation_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        double first = img.GetStandardDeviation();
        double second = img.GetStandardDeviation();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetStandardDeviation_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.True(img.GetStandardDeviation() >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetStandardDeviation() >= 0.0);
    }

    [Fact]
    public void GetStandardDeviation_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetStandardDeviation() >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_StdDevNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetStandardDeviation() >= 0.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_StdDevNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetStandardDeviation() >= 0.0);
    }
}
