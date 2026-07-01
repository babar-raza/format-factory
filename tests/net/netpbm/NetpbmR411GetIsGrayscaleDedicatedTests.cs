// Tests for NetpbmImage.GetIsGrayscale dedicated coverage.
// Sprint: ff-sprint-s393-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R411

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R411: Dedicated tests for NetpbmImage.IsGrayscale (or GetIsGrayscale()).
/// PBM returns bool.
/// PGM returns true (grayscale).
/// PPM returns false (color).
/// Width unchanged after IsGrayscale.
/// Height unchanged after IsGrayscale.
/// Format unchanged after IsGrayscale.
/// MaxValue unchanged after IsGrayscale.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM is grayscale.
/// Dogfood: 4x4 PPM is not grayscale.
/// </summary>
public class NetpbmR411GetIsGrayscaleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void IsGrayscale_PBM_ReturnsBool()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        bool result = img.IsGrayscale;
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void IsGrayscale_PGM_ReturnsTrue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.IsGrayscale);
    }

    [Fact]
    public void IsGrayscale_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.False(img.IsGrayscale);
    }

    [Fact]
    public void IsGrayscale_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.IsGrayscale;
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void IsGrayscale_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PPM);
        int before = img.Height;
        _ = img.IsGrayscale;
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void IsGrayscale_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.IsGrayscale;
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void IsGrayscale_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.IsGrayscale;
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void IsGrayscale_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        bool first = img.IsGrayscale;
        bool second = img.IsGrayscale;
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsGrayscale()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.IsGrayscale);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_IsNotGrayscale()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.False(img.IsGrayscale);
    }
}
