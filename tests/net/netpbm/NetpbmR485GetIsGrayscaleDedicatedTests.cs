// Tests for NetpbmImage.GetIsGrayscale dedicated coverage.
// Sprint: ff-sprint-s467-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R485

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R485: Dedicated tests for NetpbmImage.GetIsGrayscale().
/// PBM returns true (binary = single channel).
/// PGM returns true (grayscale).
/// PPM returns false (color).
/// Width unchanged after GetIsGrayscale.
/// Height unchanged after GetIsGrayscale.
/// Format unchanged after GetIsGrayscale.
/// MaxValue unchanged after GetIsGrayscale.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM is grayscale.
/// Dogfood: 4x4 PPM is not grayscale.
/// Dogfood: PBM is grayscale.
/// </summary>
public class NetpbmR485GetIsGrayscaleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsGrayscale_PBM_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetIsGrayscale());
    }

    [Fact]
    public void GetIsGrayscale_PGM_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetIsGrayscale());
    }

    [Fact]
    public void GetIsGrayscale_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsGrayscale());
    }

    [Fact]
    public void GetIsGrayscale_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsGrayscale_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsGrayscale_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsGrayscale_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsGrayscale_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsGrayscale();
        bool second = img.GetIsGrayscale();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_IsGrayscale()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetIsGrayscale());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_IsNotGrayscale()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsGrayscale());
    }

    [Fact]
    public void DogfoodPipeline_PBM_IsGrayscale()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetIsGrayscale());
    }
}
