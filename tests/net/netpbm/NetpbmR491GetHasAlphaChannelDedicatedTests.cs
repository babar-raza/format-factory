// Tests for NetpbmImage.GetHasAlphaChannel dedicated coverage.
// Sprint: ff-sprint-s473-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R491

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R491: Dedicated tests for NetpbmImage.GetHasAlphaChannel().
/// PBM returns false (no alpha in bitmap).
/// PGM returns false (no alpha in grayscale).
/// PPM returns false (no alpha in basic PPM).
/// Width unchanged after GetHasAlphaChannel.
/// Height unchanged after GetHasAlphaChannel.
/// Format unchanged after GetHasAlphaChannel.
/// MaxValue unchanged after GetHasAlphaChannel.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM no alpha.
/// Dogfood: 4x4 PGM no alpha.
/// Dogfood: 4x4 PPM no alpha.
/// </summary>
public class NetpbmR491GetHasAlphaChannelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHasAlphaChannel_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetHasAlphaChannel());
    }

    [Fact]
    public void GetHasAlphaChannel_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetHasAlphaChannel());
    }

    [Fact]
    public void GetHasAlphaChannel_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetHasAlphaChannel());
    }

    [Fact]
    public void GetHasAlphaChannel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetHasAlphaChannel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHasAlphaChannel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetHasAlphaChannel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHasAlphaChannel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetHasAlphaChannel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHasAlphaChannel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetHasAlphaChannel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHasAlphaChannel_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetHasAlphaChannel();
        bool second = img.GetHasAlphaChannel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NoAlpha()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetHasAlphaChannel());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NoAlpha()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetHasAlphaChannel());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NoAlpha()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetHasAlphaChannel());
    }
}
