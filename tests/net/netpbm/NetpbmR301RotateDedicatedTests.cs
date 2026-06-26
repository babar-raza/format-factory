// Tests for NetpbmImage.Rotate dedicated coverage.
// Sprint: ff-sprint-s293-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R301

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R301: Dedicated tests for NetpbmImage.Rotate(degrees).
/// Valid 90-degree call no exception.
/// Valid 180-degree call no exception.
/// Valid 270-degree call no exception.
/// All pixels in [0, MaxValue] after rotate.
/// Format unchanged after Rotate.
/// MaxValue unchanged after Rotate.
/// Rotate 360 dimensions match original.
/// Called twice no exception.
/// Dogfood: rotate 180 twice restores width and height.
/// Dogfood: rotate 90 then 270 restores original dimensions.
/// </summary>
public class NetpbmR301RotateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_90Degrees_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.Rotate(90));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_180Degrees_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.Rotate(180));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_270Degrees_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.Rotate(270));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(3, 3, 200);
        img.Rotate(90);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Rotate_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.Rotate(180);
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void Rotate_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.Rotate(90);
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void Rotate_360Degrees_DimensionsMatchOriginal()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int w = img.Width;
        int h = img.Height;
        img.Rotate(90);
        img.Rotate(90);
        img.Rotate(90);
        img.Rotate(90);
        Assert.Equal(w, img.Width);
        Assert.Equal(h, img.Height);
    }

    [Fact]
    public void Rotate_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.Rotate(90);
        var ex = Record.Exception(() => img.Rotate(90));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Rotate180Twice_RestoresDimensions()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM, 255);
        int w = img.Width;
        int h = img.Height;
        img.Rotate(180);
        img.Rotate(180);
        Assert.Equal(w, img.Width);
        Assert.Equal(h, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_Rotate90Then270_RestoresDimensions()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int w = img.Width;
        int h = img.Height;
        img.Rotate(90);
        img.Rotate(270);
        Assert.Equal(w, img.Width);
        Assert.Equal(h, img.Height);
    }
}
