// Tests for NetpbmImage.GetWhiteBalance dedicated coverage.
// Sprint: ff-sprint-s434-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R452

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R452: Dedicated tests for NetpbmImage.GetWhiteBalance().
/// Returns non-null string for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM white balance non-null.
/// </summary>
public class NetpbmR452GetWhiteBalanceDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWhiteBalance_ReturnsNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetWhiteBalance();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetWhiteBalance_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetWhiteBalance();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetWhiteBalance_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetWhiteBalance();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetWhiteBalance_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetWhiteBalance();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetWhiteBalance_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetWhiteBalance();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetWhiteBalance_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetWhiteBalance();
        string second = img.GetWhiteBalance();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetWhiteBalance_PBM_NotNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string val = img.GetWhiteBalance();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetWhiteBalance_PGM_NotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetWhiteBalance();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetWhiteBalance_PPM_NotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetWhiteBalance();
        Assert.NotNull(val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_WhiteBalanceNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetWhiteBalance();
        Assert.NotNull(val);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_WhiteBalanceNotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetWhiteBalance();
        Assert.NotNull(val);
    }
}
