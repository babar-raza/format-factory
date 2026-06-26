// Tests for NetpbmImage.Invert dedicated coverage.
// Sprint: ff-sprint-s271-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R279

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R279: Dedicated tests for NetpbmImage.Invert().
/// Valid image no exception.
/// All-zero image → all-MaxValue after invert.
/// All-MaxValue image → all-zero after invert.
/// Invert twice restores original.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice no exception.
/// Dogfood: known pixel values inverted correctly.
/// Dogfood: invert-twice original restored pixel-for-pixel.
/// </summary>
public class NetpbmR279InvertDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_ValidImage_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => img.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void Invert_AllZeroPixels_AllBecomeMaxValue()
    {
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.Pgm, 255);
        img.Invert();
        Assert.Equal(255, img.GetPixel(0, 0));
        Assert.Equal(255, img.GetPixel(1, 0));
        Assert.Equal(255, img.GetPixel(0, 1));
        Assert.Equal(255, img.GetPixel(1, 1));
    }

    [Fact]
    public void Invert_AllMaxValuePixels_AllBecomeZero()
    {
        var img = NetpbmImage.CreateNew(2, 2, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 2; r++)
            for (int c = 0; c < 2; c++)
                img.SetPixel(c, r, 255);
        img.Invert();
        Assert.Equal(0, img.GetPixel(0, 0));
        Assert.Equal(0, img.GetPixel(1, 0));
    }

    [Fact]
    public void Invert_TwiceRestoresOriginal()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 80);
        img.SetPixel(1, 1, 200);
        int orig00 = img.GetPixel(0, 0);
        int orig11 = img.GetPixel(1, 1);
        img.Invert();
        img.Invert();
        Assert.Equal(orig00, img.GetPixel(0, 0));
        Assert.Equal(orig11, img.GetPixel(1, 1));
    }

    [Fact]
    public void Invert_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.Invert();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void Invert_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.Invert();
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void Invert_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 255);
        var fmt = img.Format;
        img.Invert();
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void Invert_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 3, NetpbmFormat.Pgm, 200);
        img.Invert();
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KnownPixels_InvertedCorrectly()
    {
        var img = NetpbmImage.CreateNew(3, 2, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 0, 200);
        img.Invert();
        // 100 → 255-100=155, 200 → 255-200=55
        Assert.Equal(155, img.GetPixel(0, 0));
        Assert.Equal(55, img.GetPixel(1, 0));
    }

    [Fact]
    public void DogfoodPipeline_InvertTwice_OriginalRestored()
    {
        var img = NetpbmImage.CreateNew(4, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(3, 2, 200);
        img.SetPixel(1, 1, 50);
        int v00 = img.GetPixel(0, 0);
        int v32 = img.GetPixel(3, 2);
        int v11 = img.GetPixel(1, 1);
        img.Invert();
        img.Invert();
        Assert.Equal(v00, img.GetPixel(0, 0));
        Assert.Equal(v32, img.GetPixel(3, 2));
        Assert.Equal(v11, img.GetPixel(1, 1));
    }
}
