// Tests for NetpbmImage.GetIsTransparent dedicated coverage.
// Sprint: ff-sprint-s474-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R492

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R492: Dedicated tests for NetpbmImage.GetIsTransparent().
/// PBM returns false (no transparency in PBM format).
/// PGM returns false (no transparency in PGM format).
/// PPM returns false (no transparency in basic PPM format).
/// Width unchanged after GetIsTransparent.
/// Height unchanged after GetIsTransparent.
/// Format unchanged after GetIsTransparent.
/// MaxValue unchanged after GetIsTransparent.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM not transparent.
/// Dogfood: 4x4 PGM not transparent.
/// Dogfood: 4x4 PPM not transparent.
/// </summary>
public class NetpbmR492GetIsTransparentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsTransparent_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsTransparent());
    }

    [Fact]
    public void GetIsTransparent_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsTransparent());
    }

    [Fact]
    public void GetIsTransparent_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsTransparent());
    }

    [Fact]
    public void GetIsTransparent_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsTransparent();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsTransparent_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsTransparent();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsTransparent_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsTransparent();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsTransparent_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsTransparent();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsTransparent_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsTransparent();
        bool second = img.GetIsTransparent();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NotTransparent()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsTransparent());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NotTransparent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsTransparent());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NotTransparent()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsTransparent());
    }
}
