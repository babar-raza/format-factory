// Tests for NetpbmImage.GetIsColor dedicated coverage.
// Sprint: ff-sprint-s395-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R413

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R413: Dedicated tests for NetpbmImage.IsColor (or GetIsColor()).
/// PBM returns false (not color).
/// PGM returns false (grayscale, not color).
/// PPM returns true (color).
/// Width unchanged after IsColor.
/// Height unchanged after IsColor.
/// Format unchanged after IsColor.
/// MaxValue unchanged after IsColor.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PPM is color.
/// Dogfood: 4x4 PGM is not color.
/// </summary>
public class NetpbmR413GetIsColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void IsColor_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        Assert.False(img.IsColor);
    }

    [Fact]
    public void IsColor_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.False(img.IsColor);
    }

    [Fact]
    public void IsColor_PPM_ReturnsTrue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.IsColor);
    }

    [Fact]
    public void IsColor_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.IsColor;
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void IsColor_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PPM);
        int before = img.Height;
        _ = img.IsColor;
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void IsColor_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        NetpbmFormat before = img.Format;
        _ = img.IsColor;
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void IsColor_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int before = img.MaxValue;
        _ = img.IsColor;
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void IsColor_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        bool first = img.IsColor;
        bool second = img.IsColor;
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_IsColor()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.IsColor);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsNotColor()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.False(img.IsColor);
    }
}
