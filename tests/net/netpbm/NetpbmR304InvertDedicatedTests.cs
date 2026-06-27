// Tests for NetpbmImage.Invert dedicated coverage.
// Sprint: ff-sprint-s296-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R304

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R304: Dedicated tests for NetpbmImage.Invert().
/// Valid call no exception.
/// Pixel value becomes MaxValue minus original.
/// All pixels in [0, MaxValue] after Invert.
/// Invert twice restores original pixel values.
/// Width unchanged after Invert.
/// Height unchanged after Invert.
/// Format unchanged after Invert.
/// MaxValue unchanged after Invert.
/// Called twice no exception.
/// Dogfood: set known pixels, invert, verify inverted values.
/// </summary>
public class NetpbmR304InvertDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void Invert_PixelBecomesMaxValueMinusOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 100);
        img.Invert();
        Assert.Equal(155, img.GetPixel(2, 2)); // 255 - 100 = 155
    }

    [Fact]
    public void Invert_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(3, 3, 255);
        img.Invert();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Invert_Twice_RestoresOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 77);
        img.SetPixel(3, 2, 200);
        int v1 = img.GetPixel(1, 1);
        int v2 = img.GetPixel(3, 2);
        img.Invert();
        img.Invert();
        Assert.Equal(v1, img.GetPixel(1, 1));
        Assert.Equal(v2, img.GetPixel(3, 2));
    }

    [Fact]
    public void Invert_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.Invert();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void Invert_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.Invert();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void Invert_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.Invert();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void Invert_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.Invert();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void Invert_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.Invert();
        var ex = Record.Exception(() => img.Invert());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetKnownPixels_InvertVerifiesValues()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 200);
        img.Invert();
        Assert.Equal(205, img.GetPixel(0, 0)); // 255 - 50
        Assert.Equal(127, img.GetPixel(1, 1)); // 255 - 128
        Assert.Equal(55, img.GetPixel(2, 2));  // 255 - 200
    }
}
