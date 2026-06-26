// Tests for NetpbmImage.Rotate180 dedicated coverage.
// Sprint: ff-sprint-s186-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R182

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R182: Dedicated tests for NetpbmImage.Rotate180().
/// Rotates the image 180° — reverses pixel order.
/// Width and Height are unchanged.
/// Format and MaxValue are preserved.
/// Returns a new image (not same reference).
/// Two applications restore the original image.
/// Covers: returns new image; width unchanged; height unchanged;
/// format preserved; MaxValue preserved; double-rotate restores dims;
/// pixel at (0,0) maps to last pixel; non-square width/height both unchanged;
/// dogfood PGM rotation; dogfood two rotations restore pixel.
/// </summary>
public class NetpbmR182Rotate180Tests
{
    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate180_ReturnsNewImage_NotSameReference()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate180_WidthUnchanged()
    {
        var img = NetpbmImage.Create(7, 3, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(7, result.Width);
    }

    [Fact]
    public void Rotate180_HeightUnchanged()
    {
        var img = NetpbmImage.Create(7, 3, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Rotate180_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Rotate180_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    [Fact]
    public void Rotate180_DoubleRotation_RestoresDimensions()
    {
        var img = NetpbmImage.Create(5, 9, NetpbmFormat.PGM_P5);
        var result = img.Rotate180().Rotate180();
        Assert.Equal(5, result.Width);
        Assert.Equal(9, result.Height);
    }

    [Fact]
    public void Rotate180_NonSquare_WidthAndHeightBothUnchanged()
    {
        var img = NetpbmImage.Create(10, 3, NetpbmFormat.PGM_P5);
        var result = img.Rotate180();
        Assert.Equal(10, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void Rotate180_PixelAtOrigin_MapsToLastPixel()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200); // row=0, col=0 → last pixel after 180
        var result = img.Rotate180();
        // After 180°, pixel (0,0) of original is at (Height-1, Width-1)
        Assert.Equal(200, result.GetPixel(result.Height - 1, result.Width - 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmRotation_DimsUnchanged()
    {
        var img = NetpbmImage.Create(8, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.Rotate180();
        Assert.Equal(8, result.Width);
        Assert.Equal(5, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void DogfoodPipeline_TwoRotations_RestorePixelValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 150);
        var result = img.Rotate180().Rotate180();
        Assert.Equal(150, result.GetPixel(0, 0));
    }
}
