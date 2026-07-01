// Tests for NetpbmImage.GetIsIndexedColor dedicated coverage.
// Sprint: ff-sprint-s475-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R493

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R493: Dedicated tests for NetpbmImage.GetIsIndexedColor().
/// PBM returns false (not indexed color).
/// PGM returns false (not indexed color).
/// PPM returns false (not indexed color — direct color).
/// Width unchanged after GetIsIndexedColor.
/// Height unchanged after GetIsIndexedColor.
/// Format unchanged after GetIsIndexedColor.
/// MaxValue unchanged after GetIsIndexedColor.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM not indexed.
/// Dogfood: 4x4 PGM not indexed.
/// Dogfood: 4x4 PPM not indexed.
/// </summary>
public class NetpbmR493GetIsIndexedColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsIndexedColor_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsIndexedColor());
    }

    [Fact]
    public void GetIsIndexedColor_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsIndexedColor());
    }

    [Fact]
    public void GetIsIndexedColor_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsIndexedColor());
    }

    [Fact]
    public void GetIsIndexedColor_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsIndexedColor();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsIndexedColor_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsIndexedColor();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsIndexedColor_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsIndexedColor();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsIndexedColor_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsIndexedColor();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsIndexedColor_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsIndexedColor();
        bool second = img.GetIsIndexedColor();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NotIndexed()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsIndexedColor());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NotIndexed()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsIndexedColor());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NotIndexed()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsIndexedColor());
    }
}
