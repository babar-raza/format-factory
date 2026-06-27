// Tests for NetpbmImage.GetTotalChannelValues dedicated coverage.
// Sprint: ff-sprint-s389-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R402

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R402: Dedicated tests for NetpbmImage.GetTotalChannelValues().
/// Non-negative result.
/// Width unchanged after GetTotalChannelValues.
/// Height unchanged after GetTotalChannelValues.
/// Format unchanged after GetTotalChannelValues.
/// MaxValue unchanged after GetTotalChannelValues.
/// Idempotent (called twice same result).
/// PBM total non-negative.
/// PGM total non-negative.
/// PPM total non-negative.
/// Dogfood: 2x2 PBM total non-negative.
/// Dogfood: 4x4 PPM total non-negative.
/// </summary>
public class NetpbmR402GetTotalChannelValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTotalChannelValues_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        long total = img.GetTotalChannelValues();
        Assert.True(total >= 0);
    }

    [Fact]
    public void GetTotalChannelValues_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetTotalChannelValues();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetTotalChannelValues_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetTotalChannelValues();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetTotalChannelValues_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetTotalChannelValues();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetTotalChannelValues_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetTotalChannelValues();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetTotalChannelValues_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        long first = img.GetTotalChannelValues();
        long second = img.GetTotalChannelValues();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTotalChannelValues_PBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        long total = img.GetTotalChannelValues();
        Assert.True(total >= 0);
    }

    [Fact]
    public void GetTotalChannelValues_PGM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        long total = img.GetTotalChannelValues();
        Assert.True(total >= 0);
    }

    [Fact]
    public void GetTotalChannelValues_PPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        long total = img.GetTotalChannelValues();
        Assert.True(total >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoByTwoPBM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.PBM);
        long total = img.GetTotalChannelValues();
        Assert.True(total >= 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NonNegative()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        long total = img.GetTotalChannelValues();
        Assert.True(total >= 0);
    }
}
