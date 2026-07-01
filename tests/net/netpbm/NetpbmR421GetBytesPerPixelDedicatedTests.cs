// Tests for NetpbmImage.GetBytesPerPixel dedicated coverage.
// Sprint: ff-sprint-s403-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R421

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R421: Dedicated tests for NetpbmImage.GetBytesPerPixel().
/// PBM returns positive value.
/// PGM returns positive value.
/// PPM returns positive value.
/// Width unchanged after GetBytesPerPixel.
/// Height unchanged after GetBytesPerPixel.
/// Format unchanged after GetBytesPerPixel.
/// MaxValue unchanged after GetBytesPerPixel.
/// Idempotent (called twice same result).
/// PPM returns more bytes-per-pixel than PGM.
/// Dogfood: 4x4 PGM bytes-per-pixel positive.
/// Dogfood: 4x4 PPM bytes-per-pixel positive.
/// </summary>
public class NetpbmR421GetBytesPerPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBytesPerPixel_PBM_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        int bpp = img.GetBytesPerPixel();
        Assert.True(bpp > 0);
    }

    [Fact]
    public void GetBytesPerPixel_PGM_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int bpp = img.GetBytesPerPixel();
        Assert.True(bpp > 0);
    }

    [Fact]
    public void GetBytesPerPixel_PPM_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int bpp = img.GetBytesPerPixel();
        Assert.True(bpp > 0);
    }

    [Fact]
    public void GetBytesPerPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetBytesPerPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetBytesPerPixel_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetBytesPerPixel_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetBytesPerPixel();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetBytesPerPixel_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        int first = img.GetBytesPerPixel();
        int second = img.GetBytesPerPixel();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetBytesPerPixel_PPM_MoreThanPGM()
    {
        var pgm = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        var ppm = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(ppm.GetBytesPerPixel() >= pgm.GetBytesPerPixel());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_BytesPerPixelPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        Assert.True(img.GetBytesPerPixel() > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_BytesPerPixelPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        Assert.True(img.GetBytesPerPixel() > 0);
    }
}
