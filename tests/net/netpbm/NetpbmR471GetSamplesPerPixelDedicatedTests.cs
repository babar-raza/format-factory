// Tests for NetpbmImage.GetSamplesPerPixel dedicated coverage.
// Sprint: ff-sprint-s453-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R471

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R471: Dedicated tests for NetpbmImage.GetSamplesPerPixel().
/// PBM returns 1 (single channel binary).
/// PGM returns 1 (single channel grayscale).
/// PPM returns 3 (three channel color).
/// Width unchanged after GetSamplesPerPixel.
/// Height unchanged after GetSamplesPerPixel.
/// Format unchanged after GetSamplesPerPixel.
/// MaxValue unchanged after GetSamplesPerPixel.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM returns 1.
/// Dogfood: 4x4 PPM returns 3.
/// Dogfood: 8x8 PPM returns 3.
/// </summary>
public class NetpbmR471GetSamplesPerPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSamplesPerPixel_PBM_ReturnsOne()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.Equal(1, img.GetSamplesPerPixel());
    }

    [Fact]
    public void GetSamplesPerPixel_PGM_ReturnsOne()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal(1, img.GetSamplesPerPixel());
    }

    [Fact]
    public void GetSamplesPerPixel_PPM_ReturnsThree()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal(3, img.GetSamplesPerPixel());
    }

    [Fact]
    public void GetSamplesPerPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetSamplesPerPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSamplesPerPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetSamplesPerPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSamplesPerPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetSamplesPerPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSamplesPerPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetSamplesPerPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSamplesPerPixel_Idempotent()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int first = img.GetSamplesPerPixel();
        int second = img.GetSamplesPerPixel();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ReturnsOne()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal(1, img.GetSamplesPerPixel());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ReturnsThree()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal(3, img.GetSamplesPerPixel());
    }

    [Fact]
    public void DogfoodPipeline_EightByEightPPM_ReturnsThree()
    {
        var img = NetpbmImage.CreatePPM(8, 8, 255);
        Assert.Equal(3, img.GetSamplesPerPixel());
    }
}
