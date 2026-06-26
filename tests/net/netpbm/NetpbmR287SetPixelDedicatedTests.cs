// Tests for NetpbmImage.SetPixel dedicated coverage.
// Sprint: ff-sprint-s279-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R287

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R287: Dedicated tests for NetpbmImage.SetPixel(x, y, value).
/// Negative x throws exception.
/// Negative y throws exception.
/// Out-of-bounds x throws exception.
/// Out-of-bounds y throws exception.
/// Value below zero throws exception.
/// Value above MaxValue throws exception.
/// Valid call no exception.
/// SetPixel value retrievable by GetPixel.
/// Width unchanged after SetPixel.
/// Height unchanged after SetPixel.
/// </summary>
public class NetpbmR287SetPixelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixel_NegativeX_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        Assert.ThrowsAny<Exception>(() => img.SetPixel(-1, 0, 100));
    }

    [Fact]
    public void SetPixel_NegativeY_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        Assert.ThrowsAny<Exception>(() => img.SetPixel(0, -1, 100));
    }

    [Fact]
    public void SetPixel_OutOfBoundsX_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        Assert.ThrowsAny<Exception>(() => img.SetPixel(img.Width, 0, 100));
    }

    [Fact]
    public void SetPixel_OutOfBoundsY_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        Assert.ThrowsAny<Exception>(() => img.SetPixel(0, img.Height, 100));
    }

    [Fact]
    public void SetPixel_ValueBelowZero_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        Assert.ThrowsAny<Exception>(() => img.SetPixel(0, 0, -1));
    }

    [Fact]
    public void SetPixel_ValueAboveMaxValue_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        Assert.ThrowsAny<Exception>(() => img.SetPixel(0, 0, img.MaxValue + 1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixel_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.SetPixel(1, 1, 128));
        Assert.Null(ex);
    }

    [Fact]
    public void SetPixel_ValueRetrievableByGetPixel()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 200);
        int retrieved = img.GetPixel(2, 2);
        Assert.Equal(200, retrieved);
    }

    [Fact]
    public void SetPixel_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.SetPixel(0, 0, 50);
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void SetPixel_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.SetPixel(0, 0, 50);
        Assert.Equal(before, img.Height);
    }
}
