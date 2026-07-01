// Tests for NetpbmImage.GetIsLandscape dedicated coverage.
// Sprint: ff-sprint-s472-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R490

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R490: Dedicated tests for NetpbmImage.GetIsLandscape().
/// Landscape image (8x4 — width > height) returns true.
/// Portrait image (4x8 — height > width) returns false.
/// Square image (4x4) returns false (not landscape).
/// Width unchanged after GetIsLandscape.
/// Height unchanged after GetIsLandscape.
/// Format unchanged after GetIsLandscape.
/// MaxValue unchanged after GetIsLandscape.
/// Idempotent (called twice same result).
/// Dogfood: 8x4 PGM is landscape.
/// Dogfood: 4x8 PGM is not landscape.
/// Dogfood: 4x4 PGM is not landscape.
/// </summary>
public class NetpbmR490GetIsLandscapeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsLandscape_WiderThanTall_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        Assert.True(img.GetIsLandscape());
    }

    [Fact]
    public void GetIsLandscape_TallerThanWide_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        Assert.False(img.GetIsLandscape());
    }

    [Fact]
    public void GetIsLandscape_Square_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsLandscape());
    }

    [Fact]
    public void GetIsLandscape_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        int before = img.Width;
        _ = img.GetIsLandscape();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsLandscape_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        int before = img.Height;
        _ = img.GetIsLandscape();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsLandscape_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        string before = img.Format;
        _ = img.GetIsLandscape();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsLandscape_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsLandscape();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsLandscape_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        bool first = img.GetIsLandscape();
        bool second = img.GetIsLandscape();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_EightByFourPGM_IsLandscape()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        Assert.True(img.GetIsLandscape());
    }

    [Fact]
    public void DogfoodPipeline_FourByEightPGM_IsNotLandscape()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        Assert.False(img.GetIsLandscape());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsNotLandscape()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsLandscape());
    }
}
