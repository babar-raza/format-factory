// Tests for NetpbmImage.Resize dedicated coverage.
// Sprint: ff-sprint-s295-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R303

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R303: Dedicated tests for NetpbmImage.Resize(newWidth, newHeight).
/// Valid call no exception.
/// Resized image has expected width.
/// Resized image has expected height.
/// Format unchanged after Resize.
/// MaxValue unchanged after Resize.
/// All pixels in [0, MaxValue] after Resize.
/// Resize to same dimensions no exception.
/// Resize to 1x1 no exception.
/// Called twice no exception.
/// Dogfood: resize up then verify dimensions.
/// </summary>
public class NetpbmR303ResizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.Resize(8, 8));
        Assert.Null(ex);
    }

    [Fact]
    public void Resize_ResultHasExpectedWidth()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.Resize(6, 3);
        Assert.Equal(6, img.Width);
    }

    [Fact]
    public void Resize_ResultHasExpectedHeight()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.Resize(6, 3);
        Assert.Equal(3, img.Height);
    }

    [Fact]
    public void Resize_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.Resize(8, 8);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void Resize_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.Resize(8, 8);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void Resize_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(3, 3, 200);
        img.Resize(8, 8);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Resize_SameDimensions_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.Resize(4, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void Resize_ToOneByOne_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.Resize(1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void Resize_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.Resize(8, 8);
        var ex = Record.Exception(() => img.Resize(2, 2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ResizeUp_VerifyDimensions()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 150);
        img.Resize(12, 9);
        Assert.Equal(12, img.Width);
        Assert.Equal(9, img.Height);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
