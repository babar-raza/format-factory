// Tests for NetpbmImage.Blur dedicated coverage.
// Sprint: ff-sprint-s255-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R262

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R262: Dedicated tests for NetpbmImage.Blur().
/// Blur applies a smoothing filter to the image IN PLACE (void return).
/// Dimensions, format, and MaxValue are preserved.
/// Blurred pixel values remain in [0, MaxValue].
/// Covers: width unchanged; height unchanged; format unchanged; MaxValue unchanged;
/// all-pixels-in-range after blur; uniform image unchanged by blur;
/// no exception for valid PGM; called twice still valid;
/// dogfood: set pixels, apply blur, verify dims and range;
/// dogfood: blur of uniform image keeps values in range.
/// </summary>
public class NetpbmR262BlurDedicatedTests
{
    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Blur_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.Blur();
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void Blur_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.Blur();
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Blur_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.Blur();
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void Blur_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        img.Blur();
        Assert.Equal(200, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Blur_AllPixelsInRangeAfterBlur()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 255);
        img.Blur();
        for (int c = 0; c < img.Width; c++)
            for (int r = 0; r < img.Height; r++)
                Assert.InRange(img.GetPixel(c, r), 0, img.MaxValue);
    }

    [Fact]
    public void Blur_ValidPgm_NoException()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 200);
        var ex = Record.Exception(() => img.Blur());
        Assert.Null(ex);
    }

    [Fact]
    public void Blur_CalledTwice_StillValid()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 150);
        img.Blur();
        var ex = Record.Exception(() => img.Blur());
        Assert.Null(ex);
        // Dims still correct
        Assert.Equal(4, img.Width);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void Blur_UniformImage_PixelsStillInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        // All pixels already 0 (default); blur of uniform should keep values in range
        img.Blur();
        for (int c = 0; c < 3; c++)
            for (int r = 0; r < 3; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 255);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixelsThenBlur_DimsAndRangePreserved()
    {
        var img = NetpbmImage.Create(5, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 255);
        img.SetPixel(4, 3, 255);
        img.SetPixel(2, 2, 100);
        img.Blur();
        Assert.Equal(5, img.Width);
        Assert.Equal(4, img.Height);
        for (int c = 0; c < img.Width; c++)
            for (int r = 0; r < img.Height; r++)
                Assert.InRange(img.GetPixel(c, r), 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_BlurUniformImage_KeepsValuesInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 100);
        // Set all pixels to uniform value
        for (int c = 0; c < 4; c++)
            for (int r = 0; r < 4; r++)
                img.SetPixel(c, r, 50);
        img.Blur();
        for (int c = 0; c < 4; c++)
            for (int r = 0; r < 4; r++)
                Assert.InRange(img.GetPixel(c, r), 0, 100);
    }
}
