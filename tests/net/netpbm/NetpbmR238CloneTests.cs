// Tests for NetpbmImage.Clone dedicated coverage.
// Sprint: ff-sprint-s231-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R238

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R238: Dedicated tests for NetpbmImage.Clone().
/// Valid call returns non-null.
/// Clone is a different object (not same reference).
/// Clone has same Width.
/// Clone has same Height.
/// Clone has same Format.
/// Clone has same MaxValue.
/// Clone has same pixel values.
/// Modify clone does not affect original.
/// Clone called twice: both independent.
/// Dogfood: clone-draw-original-preserved pipeline.
/// </summary>
public class NetpbmR238CloneTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_ValidCall_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var clone = img.Clone();
        Assert.NotNull(clone);
    }

    [Fact]
    public void Clone_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var clone = img.Clone();
        Assert.NotSame(img, clone);
    }

    [Fact]
    public void Clone_SameWidth()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var clone = img.Clone();
        Assert.Equal(img.Width, clone.Width);
    }

    [Fact]
    public void Clone_SameHeight()
    {
        var img = NetpbmImage.Create(4, 7, NetpbmFormat.PGM_P5, maxValue: 255);
        var clone = img.Clone();
        Assert.Equal(img.Height, clone.Height);
    }

    [Fact]
    public void Clone_SameFormat()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        var clone = img.Clone();
        Assert.Equal(img.Format, clone.Format);
    }

    [Fact]
    public void Clone_SameMaxValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var clone = img.Clone();
        Assert.Equal(img.MaxValue, clone.MaxValue);
    }

    [Fact]
    public void Clone_SamePixelValues()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        img.SetPixel(2, 3, 200);
        var clone = img.Clone();
        Assert.Equal(img.GetPixel(1, 1), clone.GetPixel(1, 1));
        Assert.Equal(img.GetPixel(2, 3), clone.GetPixel(2, 3));
    }

    [Fact]
    public void Clone_ModifyClone_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        var clone = img.Clone();
        clone.SetPixel(0, 0, 250);
        Assert.Equal(50, img.GetPixel(0, 0));
    }

    [Fact]
    public void Clone_CalledTwice_BothIndependent()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 128);
        var clone1 = img.Clone();
        var clone2 = img.Clone();
        clone1.SetPixel(2, 2, 10);
        clone2.SetPixel(2, 2, 20);
        Assert.Equal(128, img.GetPixel(2, 2));
        Assert.Equal(10, clone1.GetPixel(2, 2));
        Assert.Equal(20, clone2.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CloneAndDraw_OriginalPreserved()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        var clone = img.Clone();
        clone.DrawLine(0, 0, 7, 7, 200);
        // Original pixel at (0,0) should remain 50
        Assert.Equal(50, img.GetPixel(0, 0));
        // Clone pixel at (0,0) should be 200 after draw
        Assert.Equal(200, clone.GetPixel(0, 0));
    }
}
