// Tests for NetpbmImage.GetBitsPerPixel dedicated coverage.
// Sprint: ff-sprint-s439-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R457

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R457: Dedicated tests for NetpbmImage.GetBitsPerPixel().
/// Returns positive int for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// PBM returns 1; PGM returns 8; PPM returns 24.
/// Dogfood: 4x4 PGM returns 8; PPM returns 24.
/// </summary>
public class NetpbmR457GetBitsPerPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBitsPerPixel_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetBitsPerPixel();
        Assert.True(val > 0);
    }

    [Fact]
    public void GetBitsPerPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBitsPerPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBitsPerPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBitsPerPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetBitsPerPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBitsPerPixel_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int first = img.GetBitsPerPixel();
        int second = img.GetBitsPerPixel();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBitsPerPixel_PBM_Returns1()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        int val = img.GetBitsPerPixel();
        Assert.Equal(1, val);
    }

    [Fact]
    public void GetBitsPerPixel_PGM_Returns8()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetBitsPerPixel();
        Assert.Equal(8, val);
    }

    [Fact]
    public void GetBitsPerPixel_PPM_Returns24()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int val = img.GetBitsPerPixel();
        Assert.Equal(24, val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_BitsPerPixelIs8()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.Equal(8, img.GetBitsPerPixel());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_BitsPerPixelIs24()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.Equal(24, img.GetBitsPerPixel());
    }
}
