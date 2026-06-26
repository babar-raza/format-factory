// Tests for NetpbmImage.Rotate dedicated coverage.
// Sprint: ff-sprint-s225-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R232

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R232: Dedicated tests for NetpbmImage.Rotate(degrees).
/// Returns new image (not same reference).
/// Format preserved.
/// MaxValue preserved.
/// All pixels in valid range after rotate.
/// Original image unchanged.
/// Rotate 0 degrees: same pixel values.
/// Rotate 360 degrees: same pixel values.
/// Rotate 90 then 270: same as original.
/// Uniform image stays uniform after rotate.
/// Dogfood: rotate chain produces valid image.
/// </summary>
public class NetpbmR232RotateTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Rotate(90);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Rotate(90);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Rotate_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 150);
        var result = img.Rotate(90);
        Assert.Equal(150, result.MaxValue);
    }

    [Fact]
    public void Rotate_AllPixelsInValidRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 15);
        img.SetPixel(0, 0, 10);
        var result = img.Rotate(90);
        for (int y = 0; y < result.Height; y++)
            for (int x = 0; x < result.Width; x++)
                Assert.InRange(result.GetPixel(x, y), 0, 15);
    }

    [Fact]
    public void Rotate_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 33);
        img.Rotate(90);
        Assert.Equal(33, img.GetPixel(0, 0));
    }

    [Fact]
    public void Rotate_ZeroDegrees_SamePixelValues()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 99);
        var result = img.Rotate(0);
        Assert.Equal(99, result.GetPixel(2, 2));
    }

    [Fact]
    public void Rotate_360Degrees_SameAsOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 77);
        var result = img.Rotate(360);
        Assert.Equal(77, result.GetPixel(1, 1));
    }

    [Fact]
    public void Rotate_UniformImage_StaysUniform()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 4; y++)
            for (int x = 0; x < 4; x++)
                img.SetPixel(x, y, 128);
        var result = img.Rotate(90);
        for (int y = 0; y < result.Height; y++)
            for (int x = 0; x < result.Width; x++)
                Assert.Equal(128, result.GetPixel(x, y));
    }

    [Fact]
    public void Rotate90Then270_SameAsOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 42);
        img.SetPixel(3, 3, 84);
        var result = img.Rotate(90).Rotate(270);
        Assert.Equal(42, result.GetPixel(0, 0));
        Assert.Equal(84, result.GetPixel(3, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RotateChain_ValidImage()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 7);
        img.SetPixel(1, 1, 5);
        var result = img.Rotate(90).Rotate(90);
        Assert.NotNull(result);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
        Assert.InRange(result.GetPixel(0, 0), 0, 7);
    }
}
