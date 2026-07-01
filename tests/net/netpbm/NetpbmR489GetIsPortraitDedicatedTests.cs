// Tests for NetpbmImage.GetIsPortrait dedicated coverage.
// Sprint: ff-sprint-s471-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R489

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R489: Dedicated tests for NetpbmImage.GetIsPortrait().
/// Portrait image (4x8 — height > width) returns true.
/// Landscape image (8x4 — width > height) returns false.
/// Square image (4x4) returns false (not portrait).
/// Width unchanged after GetIsPortrait.
/// Height unchanged after GetIsPortrait.
/// Format unchanged after GetIsPortrait.
/// MaxValue unchanged after GetIsPortrait.
/// Idempotent (called twice same result).
/// Dogfood: 4x8 PGM is portrait.
/// Dogfood: 8x4 PGM is not portrait.
/// Dogfood: 4x4 PGM is not portrait.
/// </summary>
public class NetpbmR489GetIsPortraitDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsPortrait_TallerThanWide_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        Assert.True(img.GetIsPortrait());
    }

    [Fact]
    public void GetIsPortrait_WiderThanTall_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        Assert.False(img.GetIsPortrait());
    }

    [Fact]
    public void GetIsPortrait_Square_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsPortrait());
    }

    [Fact]
    public void GetIsPortrait_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        int before = img.Width;
        _ = img.GetIsPortrait();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsPortrait_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        int before = img.Height;
        _ = img.GetIsPortrait();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsPortrait_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        string before = img.Format;
        _ = img.GetIsPortrait();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsPortrait_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        int before = img.MaxValue;
        _ = img.GetIsPortrait();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsPortrait_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        bool first = img.GetIsPortrait();
        bool second = img.GetIsPortrait();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByEightPGM_IsPortrait()
    {
        var img = NetpbmImage.CreatePGM(4, 8, 255);
        Assert.True(img.GetIsPortrait());
    }

    [Fact]
    public void DogfoodPipeline_EightByFourPGM_IsNotPortrait()
    {
        var img = NetpbmImage.CreatePGM(8, 4, 255);
        Assert.False(img.GetIsPortrait());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsNotPortrait()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsPortrait());
    }
}
