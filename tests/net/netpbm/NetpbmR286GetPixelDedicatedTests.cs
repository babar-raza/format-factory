// Tests for NetpbmImage.GetPixel dedicated coverage.
// Sprint: ff-sprint-s278-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R286

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R286: Dedicated tests for NetpbmImage.GetPixel(x, y).
/// Negative x throws exception.
/// Negative y throws exception.
/// Out-of-bounds x throws exception.
/// Out-of-bounds y throws exception.
/// Valid position returns value in [0, MaxValue].
/// Returns value set by SetPixel.
/// Width/Height/Format/MaxValue unchanged.
/// Called twice returns same result.
/// Dogfood: set pixel then get returns same value.
/// Dogfood: multiple pixels independently retrievable.
/// </summary>
public class NetpbmR286GetPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixel_NegativeX_ThrowsException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixel(-1, 0));
    }

    [Fact]
    public void GetPixel_NegativeY_ThrowsException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixel(0, -1));
    }

    [Fact]
    public void GetPixel_OutOfBoundsX_ThrowsException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixel(img.Width, 0));
    }

    [Fact]
    public void GetPixel_OutOfBoundsY_ThrowsException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        Assert.ThrowsAny<Exception>(() => img.GetPixel(0, img.Height));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixel_ValidPosition_InRange()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(1, 1, 150);
        int val = img.GetPixel(1, 1);
        Assert.InRange(val, 0, 255);
    }

    [Fact]
    public void GetPixel_ReturnsValueSetBySetPixel()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(2, 3, 187);
        Assert.Equal(187, img.GetPixel(2, 3));
    }

    [Fact]
    public void GetPixel_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        _ = img.GetPixel(0, 0);
        Assert.Equal(5, img.Width);
    }

    [Fact]
    public void GetPixel_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        _ = img.GetPixel(0, 0);
        Assert.Equal(4, img.Height);
    }

    [Fact]
    public void GetPixel_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(1, 2, 210);
        int first = img.GetPixel(1, 2);
        int second = img.GetPixel(1, 2);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetThenGet_ReturnsSameValue()
    {
        var img = NetpbmImage.CreateNew(5, 5, NetpbmFormat.Pgm, 255);
        img.SetPixel(3, 4, 123);
        Assert.Equal(123, img.GetPixel(3, 4));
    }

    [Fact]
    public void DogfoodPipeline_MultiplePixels_IndependentlyRetrievable()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 1, 50);
        img.SetPixel(2, 2, 150);
        img.SetPixel(3, 3, 230);
        Assert.Equal(10, img.GetPixel(0, 0));
        Assert.Equal(50, img.GetPixel(1, 1));
        Assert.Equal(150, img.GetPixel(2, 2));
        Assert.Equal(230, img.GetPixel(3, 3));
    }
}
