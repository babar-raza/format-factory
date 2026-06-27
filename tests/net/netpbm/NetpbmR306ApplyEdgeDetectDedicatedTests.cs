// Tests for NetpbmImage.ApplyEdgeDetect dedicated coverage.
// Sprint: ff-sprint-s298-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R306

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R306: Dedicated tests for NetpbmImage.ApplyEdgeDetect().
/// Valid call no exception.
/// All pixels in [0, MaxValue] after ApplyEdgeDetect.
/// Width unchanged after ApplyEdgeDetect.
/// Height unchanged after ApplyEdgeDetect.
/// Format unchanged after ApplyEdgeDetect.
/// MaxValue unchanged after ApplyEdgeDetect.
/// Called twice no exception.
/// All-black image no exception.
/// Dogfood: edge detect on mixed image pixels in range.
/// Dogfood: edge detect on uniform image produces valid output.
/// </summary>
public class NetpbmR306ApplyEdgeDetectDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyEdgeDetect_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.ApplyEdgeDetect());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyEdgeDetect_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(3, 3, 255);
        img.ApplyEdgeDetect();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplyEdgeDetect_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplyEdgeDetect();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplyEdgeDetect_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplyEdgeDetect();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplyEdgeDetect_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplyEdgeDetect();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplyEdgeDetect_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplyEdgeDetect();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplyEdgeDetect_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 200);
        img.ApplyEdgeDetect();
        var ex = Record.Exception(() => img.ApplyEdgeDetect());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyEdgeDetect_AllBlackImage_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        // all pixels default to 0 (black)
        var ex = Record.Exception(() => img.ApplyEdgeDetect());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_EdgeDetectPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 0, 128);
        img.SetPixel(2, 0, 200);
        img.SetPixel(3, 0, 255);
        img.ApplyEdgeDetect();
        for (int x = 0; x < 4; x++)
            Assert.InRange(img.GetPixel(x, 0), 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_ProducesValidOutput()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        // set all pixels to same value
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 128);
        img.ApplyEdgeDetect();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
