// Tests for NetpbmImage.ApplyInvert dedicated coverage.
// Sprint: ff-sprint-s326-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R338

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R338: Dedicated tests for NetpbmImage.ApplyInvert().
/// Valid call no exception.
/// Width unchanged after ApplyInvert.
/// Height unchanged after ApplyInvert.
/// Format unchanged after ApplyInvert.
/// MaxValue unchanged after ApplyInvert.
/// All pixels in valid range after ApplyInvert.
/// Invert twice restores original pixel value.
/// All-zero image becomes MaxValue after invert.
/// Dogfood: mixed pixel image dims preserved after invert.
/// Dogfood: single pixel image inverts correctly.
/// </summary>
public class NetpbmR338ApplyInvertDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyInvert_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 13) % 256);
        var ex = Record.Exception(() => img.ApplyInvert());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyInvert_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyInvert();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyInvert_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyInvert();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyInvert_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyInvert();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyInvert_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyInvert();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyInvert_AllPixelsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 11 + y * 5) % 256);
        img.ApplyInvert();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplyInvert_TwiceRestoresOriginalPixel()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 3 + y * 7) % 256);
        int original = img.GetPixel(3, 3);
        img.ApplyInvert();
        img.ApplyInvert();
        Assert.Equal(original, img.GetPixel(3, 3));
    }

    [Fact]
    public void ApplyInvert_AllZeroImage_BecomesMaxValue()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM, 255);
        img.ApplyInvert();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.Equal(img.MaxValue, img.GetPixel(x, y));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedPixelImage_DimsPreserved()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 17 + y * 23) % 256);
        img.ApplyInvert();
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
        Assert.Equal(NetpbmFormat.PGM, img.Format);
    }

    [Fact]
    public void DogfoodPipeline_SinglePixelImage_InvertsCorrectly()
    {
        var img = NetpbmImage.CreateNew(1, 1, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.ApplyInvert();
        Assert.Equal(155, img.GetPixel(0, 0));
    }
}
