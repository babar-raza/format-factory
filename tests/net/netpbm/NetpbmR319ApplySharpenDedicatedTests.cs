// Tests for NetpbmImage.ApplySharpen dedicated coverage.
// Sprint: ff-sprint-s310-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R319

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R319: Dedicated tests for NetpbmImage.ApplySharpen().
/// Valid call no exception.
/// All pixels in range [0, MaxValue] after ApplySharpen.
/// Width unchanged after ApplySharpen.
/// Height unchanged after ApplySharpen.
/// Format unchanged after ApplySharpen.
/// MaxValue unchanged after ApplySharpen.
/// Called twice no exception.
/// All-zero image returns all-in-range pixels.
/// Dogfood: mixed image pixels in range.
/// Dogfood: uniform image pixels in range.
/// </summary>
public class NetpbmR319ApplySharpenDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplySharpen_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplySharpen_AllPixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 3 + y * 7) % 256);
        img.ApplySharpen();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplySharpen_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 6, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplySharpen();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplySharpen_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 6, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplySharpen();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplySharpen_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplySharpen();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplySharpen_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplySharpen();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplySharpen_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.ApplySharpen();
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplySharpen_AllZeroImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        img.ApplySharpen();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, x % 2 == 0 ? 0 : 255);
        img.ApplySharpen();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_PixelsInRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        img.ApplySharpen();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }
}
