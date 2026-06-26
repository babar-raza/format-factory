// Tests for NetpbmImage.ApplySharpen dedicated coverage.
// Sprint: ff-sprint-s283-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R291

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R291: Dedicated tests for NetpbmImage.ApplySharpen().
/// Valid call no exception.
/// All pixels in [0, MaxValue] after ApplySharpen.
/// Width unchanged after ApplySharpen.
/// Height unchanged after ApplySharpen.
/// Format unchanged after ApplySharpen.
/// MaxValue unchanged after ApplySharpen.
/// Called twice no exception.
/// Uniform image ApplySharpen no exception.
/// Dogfood: mixed image sharpened pixels in range.
/// Dogfood: sharpen then get pixel no exception.
/// </summary>
public class NetpbmR291ApplySharpenDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplySharpen_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplySharpen_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        img.SetPixel(2, 2, 200);
        img.ApplySharpen();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplySharpen_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplySharpen();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplySharpen_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplySharpen();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplySharpen_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplySharpen();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplySharpen_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplySharpen();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplySharpen_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        img.ApplySharpen();
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplySharpen_UniformImage_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_SharpenedPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 20);
        img.SetPixel(1, 1, 100);
        img.SetPixel(2, 2, 200);
        img.SetPixel(3, 3, 240);
        img.ApplySharpen();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_SharpenThenGetPixel_NoException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 100);
        img.ApplySharpen();
        var ex = Record.Exception(() => img.GetPixel(1, 1));
        Assert.Null(ex);
    }
}
