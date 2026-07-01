// Tests for NetpbmImage.GetIsColor dedicated coverage.
// Sprint: ff-sprint-s469-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R487

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R487: Dedicated tests for NetpbmImage.GetIsColor().
/// PBM returns false (binary, not color).
/// PGM returns false (grayscale, not color).
/// PPM returns true (RGB color).
/// Width unchanged after GetIsColor.
/// Height unchanged after GetIsColor.
/// Format unchanged after GetIsColor.
/// MaxValue unchanged after GetIsColor.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM is not color.
/// Dogfood: 4x4 PGM is not color.
/// Dogfood: 4x4 PPM is color.
/// </summary>
public class NetpbmR487GetIsColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsColor_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsColor());
    }

    [Fact]
    public void GetIsColor_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsColor());
    }

    [Fact]
    public void GetIsColor_PPM_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(img.GetIsColor());
    }

    [Fact]
    public void GetIsColor_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsColor();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsColor_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsColor();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsColor_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsColor();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsColor_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsColor();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsColor_Idempotent()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        bool first = img.GetIsColor();
        bool second = img.GetIsColor();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_IsNotColor()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsColor());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsNotColor()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsColor());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_IsColor()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(img.GetIsColor());
    }
}
