// Tests for NetpbmImage.GetIsInterlaced dedicated coverage.
// Sprint: ff-sprint-s477-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R495

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R495: Dedicated tests for NetpbmImage.GetIsInterlaced().
/// PBM returns false (Netpbm formats are not interlaced).
/// PGM returns false (Netpbm formats are not interlaced).
/// PPM returns false (Netpbm formats are not interlaced).
/// Width unchanged after GetIsInterlaced.
/// Height unchanged after GetIsInterlaced.
/// Format unchanged after GetIsInterlaced.
/// MaxValue unchanged after GetIsInterlaced.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM not interlaced.
/// Dogfood: 4x4 PGM not interlaced.
/// Dogfood: 4x4 PPM not interlaced.
/// </summary>
public class NetpbmR495GetIsInterlacedDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsInterlaced_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsInterlaced());
    }

    [Fact]
    public void GetIsInterlaced_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsInterlaced());
    }

    [Fact]
    public void GetIsInterlaced_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsInterlaced());
    }

    [Fact]
    public void GetIsInterlaced_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsInterlaced();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsInterlaced_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsInterlaced();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsInterlaced_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsInterlaced();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsInterlaced_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsInterlaced();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsInterlaced_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsInterlaced();
        bool second = img.GetIsInterlaced();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NotInterlaced()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsInterlaced());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NotInterlaced()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsInterlaced());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NotInterlaced()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsInterlaced());
    }
}
