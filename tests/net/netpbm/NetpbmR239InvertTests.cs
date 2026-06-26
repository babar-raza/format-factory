// Tests for NetpbmImage.Invert dedicated coverage.
// Sprint: ff-sprint-s232-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R239

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R239: Dedicated tests for NetpbmImage.Invert().
/// Valid call returns non-null.
/// Returns different object (not same reference).
/// Format preserved after invert.
/// MaxValue preserved after invert.
/// Width preserved after invert.
/// Height preserved after invert.
/// Pixel value is MaxValue minus original pixel.
/// Uniform-max image → all pixels zero after invert.
/// Invert twice restores original pixel values.
/// Dogfood: create image, set pixels, invert, verify inversion.
/// </summary>
public class NetpbmR239InvertTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_ValidCall_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var inverted = img.Invert();
        Assert.NotNull(inverted);
    }

    [Fact]
    public void Invert_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var inverted = img.Invert();
        Assert.NotSame(img, inverted);
    }

    [Fact]
    public void Invert_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var inverted = img.Invert();
        Assert.Equal(NetpbmFormat.PGM_P5, inverted.Format);
    }

    [Fact]
    public void Invert_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var inverted = img.Invert();
        Assert.Equal(200, inverted.MaxValue);
    }

    [Fact]
    public void Invert_WidthPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var inverted = img.Invert();
        Assert.Equal(6, inverted.Width);
    }

    [Fact]
    public void Invert_HeightPreserved()
    {
        var img = NetpbmImage.Create(4, 7, NetpbmFormat.PGM_P5, maxValue: 255);
        var inverted = img.Invert();
        Assert.Equal(7, inverted.Height);
    }

    [Fact]
    public void Invert_PixelValue_IsMaxValueMinusOriginal()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        var inverted = img.Invert();
        Assert.Equal(255 - 100, inverted.GetPixel(1, 1));
    }

    [Fact]
    public void Invert_UniformMaxImage_AllPixelsZero()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        // Fill all pixels with MaxValue
        for (int x = 0; x < 4; x++)
            for (int y = 0; y < 4; y++)
                img.SetPixel(x, y, 255);
        var inverted = img.Invert();
        Assert.Equal(0, inverted.GetPixel(0, 0));
        Assert.Equal(0, inverted.GetPixel(3, 3));
    }

    [Fact]
    public void Invert_Twice_RestoresOriginalPixels()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 150);
        var invertedTwice = img.Invert().Invert();
        Assert.Equal(150, invertedTwice.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixels_Invert_VerifyAllInverted()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 0);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 255);
        var inverted = img.Invert();
        Assert.Equal(255, inverted.GetPixel(0, 0));
        Assert.Equal(255 - 128, inverted.GetPixel(1, 1));
        Assert.Equal(0, inverted.GetPixel(2, 2));
    }
}
