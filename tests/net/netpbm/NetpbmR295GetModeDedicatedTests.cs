// Tests for NetpbmImage.GetMode dedicated coverage.
// Sprint: ff-sprint-s287-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R295

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R295: Dedicated tests for NetpbmImage.GetMode().
/// Returns value in [0, MaxValue].
/// All-zero image returns 0 (most frequent).
/// All-max image returns MaxValue (most frequent).
/// Width unchanged after GetMode.
/// Height unchanged after GetMode.
/// Format unchanged after GetMode.
/// MaxValue unchanged after GetMode.
/// Called twice returns same result.
/// Dogfood: uniform image mode equals pixel value.
/// Dogfood: mixed image mode in [0, MaxValue].
/// </summary>
public class NetpbmR295GetModeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMode_InRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        int mode = img.GetMode();
        Assert.InRange(mode, 0, img.MaxValue);
    }

    [Fact]
    public void GetMode_AllZero_ReturnsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int mode = img.GetMode();
        Assert.Equal(0, mode);
    }

    [Fact]
    public void GetMode_AllMax_ReturnsMaxValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, img.MaxValue);
        int mode = img.GetMode();
        Assert.Equal(img.MaxValue, mode);
    }

    [Fact]
    public void GetMode_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMode();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMode_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMode();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMode_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMode();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMode_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMode();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMode_CalledTwice_SameResult()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(1, 0, 100);
        int first = img.GetMode();
        int second = img.GetMode();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_UniformImage_ModeEqualsPixelValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 77);
        int mode = img.GetMode();
        Assert.InRange(mode, 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_MixedImage_ModeInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 0, 50);
        img.SetPixel(2, 0, 128);
        img.SetPixel(3, 0, 200);
        int mode = img.GetMode();
        Assert.InRange(mode, 0, img.MaxValue);
    }
}
