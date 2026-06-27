// Tests for NetpbmImage.Rotate90 dedicated coverage.
// Sprint: ff-sprint-s316-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R327

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R327: Dedicated tests for NetpbmImage.Rotate90().
/// Valid call no exception.
/// All pixels in range [0, MaxValue] after Rotate90.
/// Rotate four times restores original dimensions.
/// Format unchanged after Rotate90.
/// MaxValue unchanged after Rotate90.
/// Called twice no exception.
/// All-zero image pixels still in range.
/// Pixel value preserved through four rotations.
/// Dogfood: gradient image all pixels in range.
/// Dogfood: uniform image all pixels in range.
/// </summary>
public class NetpbmR327Rotate90DedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.Rotate90());
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate90_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 15 + y * 25) % 256);
        img.Rotate90();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Rotate90_FourTimes_OriginalDimensions()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int origWidth = img.Width;
        int origHeight = img.Height;
        img.Rotate90();
        img.Rotate90();
        img.Rotate90();
        img.Rotate90();
        Assert.Equal(origWidth, img.Width);
        Assert.Equal(origHeight, img.Height);
    }

    [Fact]
    public void Rotate90_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.Rotate90();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void Rotate90_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.Rotate90();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void Rotate90_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.Rotate90();
        var ex = Record.Exception(() => img.Rotate90());
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate90_AllZeroImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.Rotate90();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Rotate90_FourTimes_PixelValuePreserved()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.SetPixel(2, 2, 150);
        int original = img.GetPixel(2, 2);
        img.Rotate90();
        img.Rotate90();
        img.Rotate90();
        img.Rotate90();
        Assert.Equal(original, img.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) * 16 % 256);
        img.Rotate90();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 100);
        img.Rotate90();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
